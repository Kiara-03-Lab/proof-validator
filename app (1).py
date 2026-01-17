"""Gradio UI for Proof Analyzer."""
import gradio as gr
import subprocess
import tempfile
import os
from pipeline import analyze_proof, format_results_as_dict
from modules import generate_graphviz_dot
from demo_proofs import DEMO_PROOF_1, DEMO_PROOF_2, DEMO_PROOF_3, DEMO_PROOF_WITH_ISSUES


def render_graph_image(graph_data: dict) -> str | None:
    """Render graph to PNG using Graphviz."""
    try:
        dot_content = generate_graphviz_dot(graph_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write(dot_content)
            dot_file = f.name
        
        png_file = dot_file.replace('.dot', '.png')
        
        result = subprocess.run(
            ['dot', '-Tpng', dot_file, '-o', png_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and os.path.exists(png_file):
            return png_file
        else:
            return None
    except Exception as e:
        print(f"Graph rendering error: {e}")
        return None


def format_steps_table(steps: list) -> str:
    """Format steps as markdown table."""
    if not steps:
        return "No steps found."
    
    lines = ["| Step | Text | Tokens | Keywords |", "|------|------|--------|----------|"]
    
    for s in steps:
        text_preview = s["text"][:100].replace("|", "\\|").replace("\n", " ")
        if len(s["text"]) > 100:
            text_preview += "..."
        tokens = ", ".join(s["tokens"][:5])
        if len(s["tokens"]) > 5:
            tokens += f" (+{len(s['tokens'])-5})"
        keywords = ", ".join(s["keywords"][:3])
        
        lines.append(f"| {s['id']} | {text_preview} | {tokens} | {keywords} |")
    
    return "\n".join(lines)


def format_assumptions_list(assumptions: list) -> str:
    """Format assumptions as markdown."""
    if not assumptions:
        return "No assumptions detected."
    
    lines = []
    for a in assumptions:
        scope_badge = "🌍 Global" if a["scope"] == "global" else "📍 Local"
        lines.append(f"### {a['id']} ({scope_badge})")
        lines.append(f"> {a['text']}")
        if a["entities"]:
            lines.append(f"**Entities:** {', '.join(a['entities'][:5])}")
        if a["properties"]:
            lines.append(f"**Properties:** {', '.join(a['properties'])}")
        lines.append(f"*Introduced at: {a['step_id']}*")
        lines.append("")
    
    return "\n".join(lines)


def format_flags_list(flags: list) -> str:
    """Format flags as markdown."""
    if not flags:
        return "✅ No issues detected!"
    
    severity_icons = {
        "low": "🟡",
        "medium": "🟠", 
        "high": "🔴"
    }
    
    lines = []
    for f in flags:
        icon = severity_icons.get(f["severity"], "⚪")
        lines.append(f"### {icon} {f['type'].replace('_', ' ').title()}")
        lines.append(f"**Location:** {f['step_id']} | **Severity:** {f['severity'].upper()}")
        lines.append(f"")
        lines.append(f"**Issue:** {f['message']}")
        lines.append(f"")
        lines.append(f"**Suggestion:** {f['suggestion']}")
        lines.append("---")
    
    return "\n".join(lines)


def analyze_and_display(latex_input: str):
    """Main analysis function for Gradio."""
    if not latex_input or not latex_input.strip():
        return (
            "Please enter a LaTeX proof.",
            "No assumptions.",
            "No analysis performed.",
            None,
            "Please enter a proof first."
        )
    
    # Run analysis
    result = analyze_proof(latex_input)
    result_dict = format_results_as_dict(result)
    
    # Format outputs
    steps_md = format_steps_table(result_dict["steps"])
    assumptions_md = format_assumptions_list(result_dict["assumptions"])
    flags_md = format_flags_list(result_dict["flags"])
    
    # Render graph
    graph_image = None
    if result_dict["graph"]["nodes"]:
        graph_image = render_graph_image(result_dict["graph"])
    
    # Summary
    summary_parts = [
        f"**Analysis Complete**",
        f"- Steps found: {len(result_dict['steps'])}",
        f"- Assumptions detected: {len(result_dict['assumptions'])}",
        f"- Issues flagged: {len(result_dict['flags'])}",
    ]
    if result_dict["errors"]:
        summary_parts.append(f"- Warnings: {', '.join(result_dict['errors'])}")
    
    summary = "\n".join(summary_parts)
    
    return steps_md, assumptions_md, flags_md, graph_image, summary


def load_demo(demo_name: str) -> str:
    """Load a demo proof."""
    demos = {
        "Lagrange's Theorem": DEMO_PROOF_1,
        "Fixed Point (Compact Space)": DEMO_PROOF_2,
        "Idempotent Operator": DEMO_PROOF_3,
        "Proof with Issues": DEMO_PROOF_WITH_ISSUES,
    }
    return demos.get(demo_name, "")


# Build UI
with gr.Blocks(title="LaTeX Proof Analyzer", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 📐 LaTeX Proof Analyzer
    
    Analyze mathematical proofs to identify steps, assumptions, potential gaps, and dependencies.
    
    **Features:**
    - Segments proofs into logical steps
    - Extracts assumptions and their scope (global vs local)
    - Flags potential issues (undefined symbols, uncited theorems, etc.)
    - Visualizes dependency graph
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            
            demo_dropdown = gr.Dropdown(
                choices=["", "Lagrange's Theorem", "Fixed Point (Compact Space)", 
                        "Idempotent Operator", "Proof with Issues"],
                label="Load Demo Proof",
                value=""
            )
            
            latex_input = gr.Textbox(
                label="LaTeX Proof",
                placeholder="Paste your LaTeX proof here...",
                lines=15,
                max_lines=30
            )
            
            analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")
            
            summary_output = gr.Markdown(label="Summary")
        
        with gr.Column(scale=2):
            gr.Markdown("### Analysis Results")
            
            with gr.Tabs():
                with gr.TabItem("📝 Steps"):
                    steps_output = gr.Markdown()
                
                with gr.TabItem("📋 Assumptions"):
                    assumptions_output = gr.Markdown()
                
                with gr.TabItem("⚠️ Gap Flags"):
                    flags_output = gr.Markdown()
                
                with gr.TabItem("🔗 Dependency Graph"):
                    graph_output = gr.Image(label="Proof Dependency Graph")
                    gr.Markdown("""
                    **Legend:**
                    - 🔵 Blue nodes: Assumptions (light blue = global, yellow = local)
                    - ⬜ White nodes: Proof steps
                    - Gray dotted: Sequential flow
                    - Blue arrows: Step uses assumption
                    - Red bold: Explicit reference to earlier step
                    """)
    
    # Event handlers
    demo_dropdown.change(
        fn=load_demo,
        inputs=[demo_dropdown],
        outputs=[latex_input]
    )
    
    analyze_btn.click(
        fn=analyze_and_display,
        inputs=[latex_input],
        outputs=[steps_output, assumptions_output, flags_output, graph_output, summary_output]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)

"""C.A.W.L. Gradio UI shell (Layer 4) — Chat, Tasks, Research, Conclave tabs.

Mounted into the FastAPI app at ``/``.
"""

from __future__ import annotations

import gradio as gr

from . import config, identity, vault, wiki
from . import brain, images, priests, scheduler, voice


def _chat_respond(message: str, history: list, image_path: str | None,
                  speak: bool, system: str) -> tuple[str, list, str | None, str | None]:
    system = system or identity.system_prompt()
    image_paths = [image_path] if image_path else None
    reply, _tools = brain.run_with_tools(system, message, image_paths)
    if speak and reply:
        try:
            audio = voice.synthesize(reply)
            audio_path = str(audio["audio"])
        except Exception:  # noqa: BLE001
            audio_path = None
    else:
        audio_path = None
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]
    return "", history, audio_path, None


def _verify_text(text: str) -> str:
    out = priests.verify(text)
    return f"**Verdict: {out['verdict']}**\n\n{out['notes']}"


def _scribe_task(task: str) -> str:
    return priests.scribe(task)


def _optikon_vision(img, question: str) -> str:
    if img is None:
        return "Attach an image first, Fabricator."
    out = priests.optikon(img, question or "Describe this image.")
    return f"**Model:** {out['model']}\n\n{out['description']}"


def _trazyn_archive(material: str) -> str:
    return priests.trazyn(material)


def _add_task(name: str, command: str, kind: str) -> str:
    if not name or not command:
        return "Both name and command are required."
    task = scheduler.add(name, command, kind)
    return f"Task `{task['id']}` scheduled ({task['kind']}) — next run {task['next_run']}."


def _task_rows() -> list[list]:
    return [[t["id"], t["name"], t["kind"], t["next_run"], t["command"]] for t in scheduler.list_tasks()]


def _refresh_tasks() -> gr.Dataframe:
    return gr.Dataframe(value=_task_rows(), headers=["id", "name", "kind", "next run", "command"], interactive=False)


def _run_task_now(task_id: str) -> str:
    result = scheduler.run_now(task_id)
    return f"{result.get('stdout', result.get('error', ''))}"


def _delete_task(task_id: str) -> str:
    return f"Deleted {task_id}." if scheduler.delete(task_id) else f"Task {task_id} not found."


def _save_research(finding: str, confidence: str, source: str) -> str:
    if not finding:
        return "A finding is required."
    vault.research_save(finding, confidence, source)
    return "Finding saved to vault/03 Research/Research Log.md"


def _wiki_append(lesson: str) -> str:
    if not lesson:
        return "A lesson is required."
    info = wiki.append(lesson)
    return f"Appended to llm-wiki ({info['entries']} entries)."


CSS = """
.gradio-container {background: #101218;}
footer {visibility: hidden;}
h1, h2, h3 {color: #e2cfaa;}
"""
THEME = gr.themes.Base()


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="C.A.W.L. — Archmagos Dominus") as demo:
        gr.HTML(
            "<div style='text-align:center;color:#e2cfaa;font-family:monospace'>"
            "⚙ C.A.W.L. — BELISARIUS CAWL · ARCHMAGOS DOMINUS · $0 RUNTIME · FREE FOREVER ⚙"
            "</div>"
        )
        with gr.Tabs():
            with gr.Tab("Chat"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(height=520, label="C.A.W.L.")
                        with gr.Row():
                            msg = gr.Textbox(placeholder="Speak to the Machine…", scale=5, container=False)
                            send = gr.Button("Send", variant="primary")
                        with gr.Row():
                            img = gr.Image(label="Attach image (optional)", type="filepath", height=120)
                            speak = gr.Checkbox(label="Speak reply", value=False)
                            system_box = gr.Textbox(label="System override (optional)", container=False)
                    with gr.Column(scale=1):
                        audio = gr.Audio(label="Voice output", type="filepath")
                        token_info = gr.Markdown(f"**Token:** `{config.CAWL_TOKEN}`")
                send.click(
                    _chat_respond,
                    inputs=[msg, chatbot, img, speak, system_box],
                    outputs=[msg, chatbot, audio, img],
                )
                msg.submit(
                    _chat_respond,
                    inputs=[msg, chatbot, img, speak, system_box],
                    outputs=[msg, chatbot, audio, img],
                )

            with gr.Tab("Tasks"):
                with gr.Row():
                    with gr.Column(scale=2):
                        task_name = gr.Textbox(label="Task name")
                        task_cmd = gr.Textbox(label="Command")
                        task_kind = gr.Dropdown(["once", "hourly", "daily", "weekly"], value="once", label="Kind")
                        task_at = gr.Textbox(label="Run at (ISO, optional for once)")
                        add_btn = gr.Button("Add task")
                        add_out = gr.Markdown("")
                    with gr.Column(scale=2):
                        refresh_btn = gr.Button("Refresh list")
                        tasks_df = gr.Dataframe(value=_task_rows(), headers=["id", "name", "kind", "next run", "command"], interactive=False)
                        with gr.Row():
                            run_id = gr.Textbox(label="Task id to run now", container=False)
                            run_btn = gr.Button("Run now")
                            del_id = gr.Textbox(label="Task id to delete", container=False)
                            del_btn = gr.Button("Delete")
                        op_out = gr.Markdown("")
                add_btn.click(_add_task, [task_name, task_cmd, task_kind], add_out)
                refresh_btn.click(_refresh_tasks, None, tasks_df)
                run_btn.click(_run_task_now, run_id, op_out)
                del_btn.click(_delete_task, del_id, op_out)

            with gr.Tab("Research"):
                with gr.Row():
                    with gr.Column(scale=2):
                        finding = gr.Textbox(label="Finding", lines=4)
                        with gr.Row():
                            conf = gr.Dropdown(["HIGH", "MEDIUM", "LOW"], value="MEDIUM", label="Confidence")
                            source = gr.Textbox(label="Source")
                        save_btn = gr.Button("Save finding")
                        save_out = gr.Markdown("")
                    with gr.Column(scale=2):
                        log_view = gr.Textbox(value=vault.list_notes("03 Research") and "See vault/03 Research", label="Research log", lines=20)
                save_btn.click(_save_research, [finding, conf, source], save_out)

            with gr.Tab("Conclave"):
                with gr.Tab("Verifier"):
                    v_in = gr.Textbox(label="Answer to review", lines=4)
                    v_btn = gr.Button("Verify")
                    v_out = gr.Markdown("")
                    v_btn.click(_verify_text, v_in, v_out)
                with gr.Tab("Scribe"):
                    s_in = gr.Textbox(label="Task for the Scribe", lines=4)
                    s_btn = gr.Button("Draft")
                    s_out = gr.Markdown("")
                    s_btn.click(_scribe_task, s_in, s_out)
                with gr.Tab("Optikon (vision)"):
                    o_img = gr.Image(label="Image", type="filepath")
                    o_q = gr.Textbox(label="Question", value="Describe this image.")
                    o_btn = gr.Button("Describe")
                    o_out = gr.Markdown("")
                    o_btn.click(_optikon_vision, [o_img, o_q], o_out)
                with gr.Tab("Trazyn (archive)"):
                    t_in = gr.Textbox(label="Material to archive", lines=4)
                    t_btn = gr.Button("Archive")
                    t_out = gr.Markdown("")
                    t_btn.click(_trazyn_archive, t_in, t_out)

            with gr.Tab("Image Forge"):
                with gr.Row():
                    with gr.Column():
                        f_kind = gr.Dropdown(["banner", "seelbon", "avatar", "map", "quote"], value="banner", label="Kind")
                        f_text = gr.Textbox(label="Text", value="C.A.W.L. — Archmagos Dominus")
                        f_color = gr.Dropdown(["mech", "bone", "steel", "gold", "abyss"], value="mech", label="Accent")
                        f_btn = gr.Button("Forge")
                    with gr.Column():
                        f_img = gr.Image(label="Result", type="filepath", height=320)
                f_btn.click(
                    lambda k, t, c: str(images.forge(k, text=t, color=c)["path"]),
                    [f_kind, f_text, f_color],
                    f_img,
                )

            with gr.Tab("Wiki"):
                with gr.Row():
                    with gr.Column():
                        w_lesson = gr.Textbox(label="New lesson", lines=3)
                        w_btn = gr.Button("Append lesson")
                        w_out = gr.Markdown("")
                    with gr.Column():
                        w_view = gr.Textbox(value=wiki.read(6000), label="llm-wiki.md", lines=26, interactive=False)
                w_btn.click(_wiki_append, w_lesson, w_out)
    demo.queue(default_concurrency_limit=4)
    return demo

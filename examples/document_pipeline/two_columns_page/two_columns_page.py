import pathlib

from tenderness import (
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    LayoutInterfaceParameters,
    Margin,
    MinimalFlexBoxTemplates,
    PDFSurfaceConfig,
    SurfaceConfigManager,
)
from tenderness.pipelines.document import (
    BlockBBoxesResult,
    DocumentBlocksConfig,
    DocumentConfig,
    DocumentRenderPipeline,
    TableBlockBBoxesResult,
    TextBlock,
    TextBlockBBoxesResult,
    TextStyle,
)

from examples.document_pipeline.helpers import SOLID_WHITE, SOLID_WOOD_BARK

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/two_columns_page/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/two_columns_page")
FONTS_DIR = pathlib.Path("font_groups/cmu")

CMU_SERIF = "CMU Serif"

LONG_TEXT = """People say reading changes you, but they mean it in the safe, book-club way — new perspective, maybe a quote for later, nothing that follows you into the corners of your thoughts when you’re not paying attention. The King in Yellow also starts safe. Act I is clean, sharp, genuinely good, the kind of thing that makes you feel like you’ve discovered hidden peak literature and now it’s your personality. You finish it thinking “this is incredible, I need more,” and that feeling doesn’t register as a red flag because why would it. Good book makes you want next part. Simple. Normal. Completely fine.
The problem is that the wanting doesn’t behave normally. It doesn’t fade, doesn’t get replaced by the next thing, just sits there like an unresolved tab in your brain. People who stop at Act I become weirdly persistent about Act II, like it’s not just curiosity but unfinished business. Meanwhile, people who actually start Act II don’t post reviews, don’t drop takes, don’t even say “mid” or “overrated,” which is statistically impossible unless something is very wrong. Instead you get fragments — notes repeating the same words, references to places that sound fake but are described with full confidence, sentences that start like explanations and end like they forgot who explanations are for.
It’s not even dramatic. No “I have seen the truth” speeches. Just a slow drift from “this book is amazing” to “why does that symbol feel familiar” to “Carcosa sounds kinda real actually” and then nothing. Not silence in a mysterious, cinematic way, just the complete absence of follow-up, like the conversation got deleted. And the creepiest part is how consistent it is. Different people, same pattern, same drift, same disappearance of anything you could call a conclusion. It doesn’t feel like coincidence, it feels like convergence, like everyone is being gently routed to the same place without comparing notes.
Meanwhile, you’re still there with Act I brain, thinking you’re built different, thinking you’ll just read Act II “carefully,” like it’s spicy food and not whatever this is. Your brain hates the gap, hates that there’s a missing piece where the explanation should be, keeps trying to resolve it because that’s what brains do. And the book doesn’t stop you. No warnings, no locks, no “are you sure?” prompt. Just pages. Same as any other book. Turn one, then another, same motion, same logic, nothing visibly different.
And that’s the whole trick. It never feels like a bad decision while you’re making it. It feels obvious, justified, even smart. Of course you continue. Of course you want to see how it ends. Of course you think you’ll be the one who reads it and comes back with a clean summary like “yeah it’s about X, kinda overrated tbh.” Everyone thinks that. There is no evidence for it, but that doesn’t matter, because the structure of the first act teaches you to expect coherence, to expect payoff, to trust that the pattern will close.
But the pattern doesn’t close. It just… stops being something you can describe. And by the time you realize that’s what’s happening, you’re already past the point where “realizing” helps. The page is still there. You can still turn it. Nothing is physically stopping you.
Which is exactly why people keep doing it."""  # noqa: RUF001

surface_config_manager = SurfaceConfigManager()

PDF_SURFACE_CONFIG = surface_config_manager.create_pdf_surface_config(
    width=612,
    height=792,
)


def _setup_fonts() -> None:
    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=OUTPUT_DIR / "fontconfig_file",
    )


def render_two_columns_page(
    surface_config: PDFSurfaceConfig,
) -> tuple[
    list[TextBlockBBoxesResult | TableBlockBBoxesResult | None],
    BlockBBoxesResult,
]:
    # 1) Setup custom fonts
    _setup_fonts()

    # 2) Define layout
    document_config = DocumentConfig(
        surface_config=surface_config,
        global_margin=Margin(top=45, right=30, bottom=45, left=30),
        block_spec=MinimalFlexBoxTemplates.flow_templates.flow_columns(specs=2, gap=20),
        background_spec=SOLID_WHITE,
    )
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            TextBlock(block_name="col_1", text=LONG_TEXT),
            TextBlock(block_name="col_2"),
        ],
        base_text_style=TextStyle(
            font_description_params=FontDescriptionInterfaceParameters(family=CMU_SERIF, size_device_units=12),
            text_color_spec=SOLID_WOOD_BARK,
            layout_interface_params=LayoutInterfaceParameters(justify=True, wrap="word-char"),
        ),
    )

    # 3) Render
    render_pipeline = DocumentRenderPipeline()
    setup_result = render_pipeline.setup(config=document_config)
    render_result = render_pipeline.render(blocks_config=blocks_config, setup_result=setup_result)

    # 4) Extract bounding boxes
    text_bboxes = render_pipeline.get_text_bounding_boxes(
        rendered_blocks=render_result.rendered_blocks,
    )
    block_bboxes = render_pipeline.get_block_bounding_boxes(
        setup_result=setup_result,
    )

    # 5) Save
    output_path = OUTPUT_DIR / f"two_columns_page{surface_config.image_format.extension}"
    render_pipeline.save_as_file(
        surface=setup_result.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup_result.stream,
    )

    return text_bboxes, block_bboxes


if __name__ == "__main__":
    for surface_config in [PDF_SURFACE_CONFIG]:
        text_bboxes, block_bboxes = render_two_columns_page(surface_config)
        print(f"Saved → {OUTPUT_DIR}/two_columns_page{surface_config.image_format.extension}")

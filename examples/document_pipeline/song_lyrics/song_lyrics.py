import pathlib

from tenderness import (
    DashStyle,
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImageSurfaceConfig,
    LayoutInterfaceParameters,
    Margin,
    MinimalDraw,
    MinimalFlexBoxTemplates,
    PDFSurfaceConfig,
    StrokeStyle,
    SurfaceConfigManager,
    SVGSurfaceConfig,
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

from examples.document_pipeline.helpers import (
    LG_DUSK_CANOPY,
    LG_ROYAL_SMOKE,
    NAMIBIA,
    NINJA_PRINCESS,
    SOLID_PAPAYA_WHIP,
    SOLID_WOOD_BARK,
    WOOD_BARK,
)

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/song_lyrics/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/song_lyrics")
FONTS_DIR = pathlib.Path("font_groups/dm")

DM_SERIF_DISPLAY = "DM Serif Display"
DM_SANS = "DM Sans"

SONG_TITLE_MARKUP = (
    f'<span font_desc="{DM_SERIF_DISPLAY} 36" foreground="{WOOD_BARK.hex}">'
    f'<b>Old MacDonald</b><i> <span foreground="{NINJA_PRINCESS.hex}">Had a Farm</span></i></span>'
    f'<span font_desc="{DM_SANS} 13" foreground="{NAMIBIA.hex}">'
    f"\nA beloved children's song for all ages 🐄 🐷 🦆 🐔</span>"
)

VERSE_1_LABEL = "Verse 1 — The Cow 🐄"
VERSE_1 = (
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "And on his farm he had a cow, E-I-E-I-O!\n"
    "With a moo-moo here, and a moo-moo there,\n"
    "Here a moo, there a moo, everywhere a moo-moo!\n"
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "🐄🐄🐄"
)

VERSE_2_LABEL = "Verse 2 — The Pig 🐷"
VERSE_2 = (
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "And on his farm he had a pig, E-I-E-I-O!\n"
    "With an oink-oink here, and an oink-oink there,\n"
    "Here an oink, there an oink, everywhere an oink-oink!\n"
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "🐷🐷🐷"
)

VERSE_3_LABEL = "Verse 3 — The Duck 🦆"
VERSE_3 = (
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "And on his farm he had a duck, E-I-E-I-O!\n"
    "With a quack-quack here, and a quack-quack there,\n"
    "Here a quack, there a quack, everywhere a quack-quack!\n"
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "🦆🦆🦆"
)

VERSE_4_LABEL = "Verse 4 — The Chicken 🐔"
VERSE_4 = (
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "And on his farm he had a chicken, E-I-E-I-O!\n"
    "With a cluck-cluck here, and a cluck-cluck there,\n"
    "Here a cluck, there a cluck, everywhere a cluck-cluck!\n"
    "Old MacDonald had a farm, E-I-E-I-O!\n"
    "🐔🐔🐔"
)

surface_config_manager = SurfaceConfigManager()

IMG_SURFACE_CONFIG = surface_config_manager.create_image_surface_config(
    width=1280,
    height=720,
)
SVG_SURFACE_CONFIG = surface_config_manager.create_svg_surface_config(
    width=1280,
    height=720,
)
PDF_SURFACE_CONFIG = surface_config_manager.create_pdf_surface_config(
    width=1280,
    height=720,
)


def _setup_fonts() -> None:
    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=OUTPUT_DIR / "fontconfig_file",
    )


def render_song_lyrics(
    surface_config: ImageSurfaceConfig | SVGSurfaceConfig | PDFSurfaceConfig,
) -> tuple[
    list[TextBlockBBoxesResult | TableBlockBBoxesResult | None],
    BlockBBoxesResult,
]:
    # 1) Setup custom fonts
    _setup_fonts()

    # 2) Define layout
    document_config = DocumentConfig(
        surface_config=surface_config,
        global_margin=Margin(top=10, right=30, bottom=10, left=30),
        block_spec=MinimalFlexBoxTemplates.documents_templates.header_labeled_sections(
            header_height=110,
            section_label_height=40,
            col_specs=2,
            n_sections=2,
            header_gap=5,
            section_gap=10,
            col_gap=10,
        ),
        background_spec=LG_DUSK_CANOPY,
    )
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            TextBlock(
                block_name="header",
                text=SONG_TITLE_MARKUP,
                text_strategy="markup",
                text_style=TextStyle(layout_interface_params=LayoutInterfaceParameters(alignment="center")),
            ),
            TextBlock(block_name="col_0_section_0_label", text=VERSE_1_LABEL),
            TextBlock(block_name="col_0_section_0_content", text=VERSE_1),
            TextBlock(block_name="col_0_section_1_label", text=VERSE_2_LABEL),
            TextBlock(block_name="col_0_section_1_content", text=VERSE_2),
            TextBlock(block_name="col_1_section_0_label", text=VERSE_3_LABEL),
            TextBlock(block_name="col_1_section_0_content", text=VERSE_3),
            TextBlock(block_name="col_1_section_1_label", text=VERSE_4_LABEL),
            TextBlock(block_name="col_1_section_1_content", text=VERSE_4),
        ],
        base_text_style=TextStyle(
            font_description_params=FontDescriptionInterfaceParameters(family=DM_SERIF_DISPLAY, size=18),
            text_color_spec=SOLID_WOOD_BARK,
        ),
    )

    # 3) Setup render pipeline
    render_pipeline = DocumentRenderPipeline()
    setup_result = render_pipeline.setup(config=document_config)

    # 4) Draw decorations before text is rendered

    header_rect = setup_result.block_positions[0].rect
    minimal_draw = MinimalDraw()

    # Draw rounded rect background and border for header block
    minimal_draw.shapes.rounded_rect(
        cairo_context=setup_result.cairo_context,
        rect=header_rect,
        color_spec=SOLID_PAPAYA_WHIP,
        color_model=surface_config.color_model,
        radius=10,
    )
    minimal_draw.borders.rounded_rect(
        cairo_context=setup_result.cairo_context,
        rect=header_rect,
        color_spec=LG_ROYAL_SMOKE,
        color_model=surface_config.color_model,
        radius=10,
        stroke=StrokeStyle(line_width=3, dash_style=DashStyle.SOLID),
    )

    # 5) Render text
    render_result = render_pipeline.render(blocks_config=blocks_config, setup_result=setup_result)

    # 6) Extract bounding boxes
    text_bboxes = render_pipeline.get_text_bounding_boxes(
        rendered_blocks=render_result.rendered_blocks,
    )
    block_bboxes = render_pipeline.get_block_bounding_boxes(
        setup_result=setup_result,
    )

    # 7) Save
    output_path = OUTPUT_DIR / f"song_lyrics{surface_config.image_format.extension}"
    render_pipeline.save_as_file(
        surface=setup_result.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup_result.stream,
    )

    return text_bboxes, block_bboxes


if __name__ == "__main__":
    configs: list[ImageSurfaceConfig | SVGSurfaceConfig | PDFSurfaceConfig] = [
        IMG_SURFACE_CONFIG,
        SVG_SURFACE_CONFIG,
        PDF_SURFACE_CONFIG,
    ]
    for surface_config in configs:
        text_bboxes, block_bboxes = render_song_lyrics(surface_config=surface_config)
        print(f"Saved → {OUTPUT_DIR}/song_lyrics{surface_config.image_format.extension}")

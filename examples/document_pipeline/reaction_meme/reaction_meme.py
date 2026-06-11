import pathlib

from tenderness import (
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImagePatternSpec,
    ImageSurfaceConfig,
    LayoutInterfaceParameters,
    Margin,
    MinimalFlexBoxTemplates,
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

from examples.document_pipeline.helpers import SOLID_BLACK

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/reaction_meme/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/reaction_meme")
FONTS_DIR = pathlib.Path("font_groups/noto")
IMAGE_PATH = pathlib.Path("images/reaction_meme_800_1200.png")

NOTO_SANS = "Noto Sans"

PANEL_TEXTS = [
    "Renders text in synthetic documents",
    "Does it fast",
    "Exact bounding boxes at multiple levels",
    "In any \nラんgüאج",
]

PANEL_HEIGHTS = [
    285.0,
    285.0,
    290.0,
    320.0,
]  # total height per panel (must sum to surface_height - top - bottom margin)
PANEL_OFFSETS: list[float | None] = [0.0, 80.0, 0.0, 80.0]  # top spacer per panel — increase to push text lower

PANEL_NAMES = [f"panel_{i}" for i in range(len(PANEL_TEXTS))]
SPACER_NAMES = [f"spacer_{i}" for i in range(len(PANEL_TEXTS))]

CENTERED_LAYOUT = LayoutInterfaceParameters(alignment="center")

MEME_TEXT_STYLE = TextStyle(
    font_description_params=FontDescriptionInterfaceParameters(family=NOTO_SANS, size=38, weight="bold"),
    text_color_spec=SOLID_BLACK,
    layout_interface_params=CENTERED_LAYOUT,
)

surface_config_manager = SurfaceConfigManager()

IMG_SURFACE_CONFIG = surface_config_manager.create_image_surface_config(
    width=800,
    height=1200,
)


def _setup_fonts() -> None:
    font_setup = FontSetup()
    font_setup.setup_font(
        mode=FontconfigMode.TEMPLATE_MINIMAL,
        font_dir=FONTS_DIR,
        fontconfig_destination_dir=OUTPUT_DIR / "fontconfig_file",
    )


def render_reaction_meme(
    surface_config: ImageSurfaceConfig,
) -> tuple[
    list[TextBlockBBoxesResult | TableBlockBBoxesResult | None],
    BlockBBoxesResult,
]:
    # 1) Setup custom fonts
    _setup_fonts()

    # 2) Define layout
    document_config = DocumentConfig(
        surface_config=surface_config,
        global_margin=Margin(top=10, right=415, bottom=10, left=5),
        block_spec=MinimalFlexBoxTemplates.documents_templates.labeled_sections(
            section_label_height=PANEL_OFFSETS,
            section_content_height=[
                h - (o if o is not None else 0.0) for h, o in zip(PANEL_HEIGHTS, PANEL_OFFSETS, strict=True)
            ],
            col_specs=1,
            n_sections=len(PANEL_TEXTS),
            names=[name for pair in zip(SPACER_NAMES, PANEL_NAMES, strict=True) for name in pair],
        ),
        background_spec=ImagePatternSpec(path=IMAGE_PATH),
    )

    # 3) Build blocks — one TextBlock per meme panel
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            block
            for spacer_name, panel_name, text in zip(SPACER_NAMES, PANEL_NAMES, PANEL_TEXTS, strict=True)
            for block in (
                TextBlock(block_name=spacer_name, text=""),
                TextBlock(block_name=panel_name, text=text, text_style=MEME_TEXT_STYLE),
            )
        ],
    )

    # 4) Render
    render_pipeline = DocumentRenderPipeline()
    setup_result = render_pipeline.setup(config=document_config)
    render_result = render_pipeline.render(blocks_config=blocks_config, setup_result=setup_result)

    # 5) Extract bounding boxes
    text_bboxes = render_pipeline.get_text_bounding_boxes(
        rendered_blocks=render_result.rendered_blocks,
    )
    block_bboxes = render_pipeline.get_block_bounding_boxes(
        setup_result=setup_result,
    )

    # 6) Save
    output_path = OUTPUT_DIR / f"reaction_meme{surface_config.image_format.extension}"
    render_pipeline.save_as_file(
        surface=setup_result.surface,
        surface_config=surface_config,
        output_file_path=output_path,
        stream=setup_result.stream,
    )

    return text_bboxes, block_bboxes


if __name__ == "__main__":
    for surface_config in [IMG_SURFACE_CONFIG]:
        text_bboxes, block_bboxes = render_reaction_meme(surface_config)
        print(f"Saved → {OUTPUT_DIR}/reaction_meme{surface_config.image_format.extension}")

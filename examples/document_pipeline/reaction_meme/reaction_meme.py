import pathlib

from tenderness import (
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImagePatternSpec,
    ImageSurfaceConfig,
    LayoutInterfaceParameters,
    Rectangle,
    SurfaceConfigManager,
)
from tenderness.pipelines.document import (
    BlockBBoxesResult,
    BlockPosition,
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

BLOCK_POSITIONS = [
    BlockPosition(name="panel_0", rect=Rectangle(x=5, y=10, width=380, height=285)),
    BlockPosition(name="panel_1", rect=Rectangle(x=5, y=375, width=380, height=205)),
    BlockPosition(name="panel_2", rect=Rectangle(x=5, y=580, width=380, height=290)),
    BlockPosition(name="panel_3", rect=Rectangle(x=5, y=950, width=380, height=240)),
]

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
        block_spec=BLOCK_POSITIONS,
        background_spec=ImagePatternSpec(path=IMAGE_PATH),
    )

    # 3) Build blocks — one TextBlock per meme panel
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[
            TextBlock(block_name=bp.name, text=text, text_style=MEME_TEXT_STYLE)
            for bp, text in zip(BLOCK_POSITIONS, PANEL_TEXTS, strict=True)
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

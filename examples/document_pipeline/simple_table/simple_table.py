import pathlib

from tenderness import (
    CaptionSpec,
    FontconfigMode,
    FontDescriptionInterfaceParameters,
    FontSetup,
    ImageSurfaceConfig,
    LayoutInterfaceParameters,
    Margin,
    MinimalDraw,
    MinimalFlexBoxTemplates,
    PDFSurfaceConfig,
    SurfaceConfigManager,
    SVGSurfaceConfig,
)
from tenderness.pipelines.document import (
    BlockBBoxesResult,
    DocumentBlocksConfig,
    DocumentConfig,
    DocumentRenderPipeline,
    TableBlock,
    TableBlockBBoxesResult,
    TableBlockHelpers,
    TextBlockBBoxesResult,
    TextCell,
    TextStyle,
)

from examples.document_pipeline.helpers import IMP_COFFEE, SOLID_PAPAYA_WHIP, SOLID_WHITE, SOLID_WOOD_BARK

EXAMPLE_DIR = pathlib.Path("examples/document_pipeline/simple_table/")
OUTPUT_DIR = pathlib.Path("examples_output/document_pipeline/simple_table")
FONTS_DIR = pathlib.Path("font_groups/dm")

DM_SERIF_DISPLAY = "DM Serif Display"
DM_SANS = "DM Sans"

CENTERED_LAYOUT = LayoutInterfaceParameters(alignment="center")

HEADER_STYLE = TextStyle(
    font_description_params=FontDescriptionInterfaceParameters(family=DM_SANS, size=28, weight="bold"),
    text_color_spec=SOLID_WOOD_BARK,
    layout_interface_params=CENTERED_LAYOUT,
)
CELLS_STYLE = TextStyle(
    font_description_params=FontDescriptionInterfaceParameters(family=DM_SANS, size=20, weight="bold"),
    text_color_spec=IMP_COFFEE,
    layout_interface_params=CENTERED_LAYOUT,
)
CAPTION_STYLE = TextStyle(
    font_description_params=FontDescriptionInterfaceParameters(
        family=DM_SERIF_DISPLAY, size=24, weight="bold", style="italic"
    ),
    text_color_spec=SOLID_WOOD_BARK,
    layout_interface_params=CENTERED_LAYOUT,
)

TABLE_CELLS = [
    TextCell(text="Coffee Type", cell_name="my_header_1", text_style=HEADER_STYLE),
    TextCell(text="Origin", cell_name="my_header_2", text_style=HEADER_STYLE),
    TextCell(text="Flavor Notes", cell_name="my_header_3", text_style=HEADER_STYLE),
    TextCell(text="Pour Over", cell_name="my_row1_col1"),
    TextCell(text="Ethiopia 🇪🇹", cell_name="my_row1_col2"),
    TextCell(text="Floral, citrus, tea-like", cell_name="my_row1_col3"),
    TextCell(text="Espresso", cell_name="my_row2_col1"),
    TextCell(text="Colombia 🇨🇴", cell_name="my_row2_col2"),
    TextCell(text="Chocolatey, nutty, balanced", cell_name="my_row2_col3"),
    TextCell(
        text="Table 1. Coffee is all you need ☕",
        cell_name="my_table_caption",
        text_style=CAPTION_STYLE,
    ),
]

HEADER_CELL_NAMES = {cell.cell_name for cell in TABLE_CELLS if cell.text_style is HEADER_STYLE}
TABLE_CELL_NAMES: list[str] = [
    cell.cell_name for cell in TABLE_CELLS if cell.cell_name is not None and cell.cell_name != "my_table_caption"
]

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


def render_simple_table(
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
        global_margin=Margin(top=230, right=10, bottom=230, left=10),
        background_spec=SOLID_WHITE,
    )
    table_block = TableBlock(
        block_name="my_simple_table",
        cells=TABLE_CELLS,
        table_cell_pos=MinimalFlexBoxTemplates.table_templates.table_header_basic(
            row_specs=2,
            col_specs=3,
            header_height=60,
            caption=CaptionSpec(height=100, gap=10, name="my_simple_table_caption"),
            names=TABLE_CELL_NAMES,
        ),
        base_text_style=CELLS_STYLE,
    )
    blocks_config = DocumentBlocksConfig(
        surface_config=surface_config,
        blocks=[table_block],
    )

    # 3) Setup render pipeline
    render_pipeline = DocumentRenderPipeline()
    setup_result = render_pipeline.setup(config=document_config)

    # 4) Draw cell decorations before text is rendered
    minimal_draw = MinimalDraw()
    cell_positions = TableBlockHelpers.create_cells_within_container(
        minimal_flexbox_engine=render_pipeline.minimal_flexbox_engine,
        container_rect=setup_result.block_positions[0].rect,
        node=table_block.table_cell_pos,
    )
    for cell_pos in cell_positions:
        if cell_pos.name in HEADER_CELL_NAMES:
            # Draw white background for header cells
            minimal_draw.shapes.rect(
                cairo_context=setup_result.cairo_context,
                rect=cell_pos.rect,
                color_spec=SOLID_PAPAYA_WHIP,
                color_model=surface_config.color_model,
            )
            # Draw borders for header cells
            minimal_draw.borders.rect(
                cairo_context=setup_result.cairo_context,
                rect=cell_pos.rect,
                color_spec=SOLID_WOOD_BARK,
                color_model=surface_config.color_model,
            )
        if cell_pos.name and "row" in cell_pos.name:
            # Draw borders for regular cells
            minimal_draw.borders.rect(
                cairo_context=setup_result.cairo_context,
                rect=cell_pos.rect,
                color_spec=SOLID_WOOD_BARK,
                color_model=surface_config.color_model,
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
    output_path = OUTPUT_DIR / f"simple_table{surface_config.image_format.extension}"
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
        text_bboxes, block_bboxes = render_simple_table(surface_config=surface_config)
        print(f"Saved → {OUTPUT_DIR}/simple_table{surface_config.image_format.extension}")

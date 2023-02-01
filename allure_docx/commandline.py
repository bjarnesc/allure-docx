import os
import click
from allure_docx.report_builder import ReportBuilder
from allure_docx.config import ReportConfig
from allure_docx.config import CONFIG_TAGS


@click.command()
@click.argument("allure_dir")
@click.argument("output")
@click.option(
    "--template",
    default=None,
    help="Path (absolute or relative) to a custom docx template file with styles",
)
@click.option(
    "--config_tag",
    default=None,
    type=click.Choice(CONFIG_TAGS),
    help="Configuration tag for the docx report.",
)
@click.option(
    "--config_path",
    default=None,
    type=click.Path(exists=True, resolve_path=True),
    help="Path to custom .ini configuration file (see documentation).",
)
@click.option(
    "--pdf",
    is_flag=True,
    help="Try to generate a pdf file from created docx using soffice or OfficeToPDF (needs MS Word installed)",
)
@click.option("--title", default=None, help="Custom report title")
@click.option("--logo", default=None, help="Path to custom report logo image")
@click.option(
    "--logo-width",
    default=None,
    help="Image width in centimeters. Width is scaled to keep aspect ratio",
)
def main(allure_dir, output, template, pdf, title, logo, logo_width, config_tag, config_path):
    """allure_dir: Path (relative or absolute) to allure_dir folder with test results

    output: Path (relative or absolute) with filename for the generated docx file"""

    def build_config():
        """
        builds the config by creating a ReportConfig object and adding additional configuration variables.
        """
        _config = ReportConfig()
        if config_tag and config_path:
            raise click.UsageError("Cannot define both config_path and config option.")
        elif config_tag:
            script_path = os.path.dirname(os.path.realpath(__file__))
            config = script_path + "/config/" + config_tag + ".ini"
        elif config_path:
            if not config_path.endswith(".ini"):
                raise click.UsageError("Given config path is not an ini file.")
            config = config_path
        else:
            script_path = os.path.dirname(os.path.realpath(__file__))
            config = script_path + "/config/standard.ini"
        _config.read_config_from_file(config)

        if logo:
            _config['logo'] = {}
            _config['logo']['path'] = logo
            if logo_width:
                _config['logo']['width'] = logo_width
        if template:
            _config['template_path'] = template
        if 'title' not in _config['cover']:
            _config['cover']['title'] = title
        return _config

    cwd = os.getcwd()

    if not os.path.isabs(allure_dir):
        allure_dir = os.path.join(cwd, allure_dir)
    if not os.path.isabs(output):
        output = os.path.join(cwd, output)
    elif template and not os.path.isabs(template):
        template = os.path.join(cwd, template)
    print(f"Template: {template}")

    if logo_width is not None:
        logo_width = float(logo_width)

    report_config = build_config()
    report_builder = ReportBuilder(allure_dir=allure_dir, config=report_config)
    report_builder.save_report(output)

    if pdf:
        pdf_name, ext = os.path.splitext(output)
        pdf_name += ".pdf"
        report_builder.save_report_to_pdf(pdf_name)


if __name__ == "__main__":
    main()

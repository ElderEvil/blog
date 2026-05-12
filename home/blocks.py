from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class BodyBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(form_classname="title", icon="title")
    paragraph = blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul", "code"])
    image = ImageChooserBlock()
    embed = EmbedBlock()
    code = blocks.TextBlock(
        icon="code",
        template="blocks/code.html",
    )

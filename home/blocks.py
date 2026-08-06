from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailcodeblock.blocks import CodeBlock


class BodyBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        template="blocks/heading.html",
    )
    paragraph = blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul", "code"])
    image = ImageChooserBlock(template="blocks/image.html")
    embed = EmbedBlock()
    code = CodeBlock(label="Code")

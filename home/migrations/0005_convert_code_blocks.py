# Converts wagtailcodeblock CodeBlock (StructBlock: language+code) → plain CharBlock.
# Transforms body StreamField JSON: replaces {type: "code", value: {language: X, code: Y}}
# with {type: "code", value: Y}.

from django.db import migrations


def convert_code_blocks(apps, schema_editor):
    BlogPage = apps.get_model("home", "BlogPage")
    for page in BlogPage.objects.filter(body__len__gt=0).only("body"):
        raw = page.body.raw_data
        if not raw:
            continue
        new_blocks = []
        changed = False
        for block in raw:
            block_type = block.get("type", "")
            value = block.get("value")
            # wagtailcodeblock CodeBlock stored a dict: {"language": ..., "code": ...}
            if block_type == "code" and isinstance(value, dict) and "code" in value:
                value = value["code"]
                changed = True
            new_blocks.append({"type": block_type, "value": value})
        if changed:
            page.body = new_blocks
            page.save(update_fields=["body"])


def reverse_code_blocks(apps, schema_editor):
    BlogPage = apps.get_model("home", "BlogPage")
    for page in BlogPage.objects.filter(body__len__gt=0).only("body"):
        raw = page.body.raw_data
        if not raw:
            continue
        new_blocks = []
        changed = False
        for block in raw:
            block_type = block.get("type", "")
            value = block.get("value")
            if block_type == "code" and isinstance(value, str):
                value = {"language": "none", "code": value}
                changed = True
            new_blocks.append({"type": block_type, "value": value})
        if changed:
            page.body = new_blocks
            page.save(update_fields=["body"])


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0004_alter_blogpage_body"),
    ]

    operations = [
        migrations.RunPython(convert_code_blocks, reverse_code_blocks),
    ]
from plone.restapi.behaviors import IBlocks
from plone.restapi.blocks import iter_block_transform_handlers, visit_blocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IFieldDeserializer
from plone.schema import IJSONField
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.dexterity.interfaces import IDexterityContent


@implementer(IFieldDeserializer)
@adapter(IJSONField, IDexterityContent, IBrowserRequest)
class CPBlocksJSONFieldDeserializer(DefaultFieldDeserializer):
    """Copy of the plone.restapi blocks deserializer that iterates over each slot"""

    def __call__(self, value):
        value = super().__call__(value)
        if self.field.getName() == "volto_slots_editor_controlpanel_data":
            for slot_value in value.values():
                slot_blocks = slot_value.get("blocks")
                if not slot_blocks:
                    continue
                for block in visit_blocks(self.context, slot_blocks):
                    new_block = block.copy()
                    for handler in iter_block_transform_handlers(
                        self.context, block, IBlockFieldDeserializationTransformer
                    ):
                        new_block = handler(new_block)
                    block.clear()
                    block.update(new_block)
        return value

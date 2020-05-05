from typing import Sequence, List

from pyrsistent import PRecord, field

from pyshgp.push.config import PushConfig
from pyshgp.push.atoms import CodeBlock
from pyshgp.utils import Saveable


class ProgramSignature(PRecord):
    arity = field(type=int, mandatory=True)
    output_stacks = field(type=list, mandatory=True)
    push_config = field(type=PushConfig, mandatory=True)


class Program(Saveable, PRecord):
    code = field(type=CodeBlock, mandatory=True)
    signature = field(type=ProgramSignature, mandatory=True)


# class ProgramSignature:
#     """A collection of values required to get consistent behavior from Push code."""
#
#     def __init__(self, arity: int, output_stacks: Sequence[str], push_config: PushConfig):
#         self.arity = arity
#         self.output_stacks = output_stacks
#         self.push_config = push_config


# class Program(Saveable):
#     """A Push program composed of some Push code and a ProgramSignature."""
#
#     def __init__(self, code: CodeBlock, signature: ProgramSignature):
#         self.code = code
#         self.signature = signature
#
#     def __repr__(self):
#         return "Program[{arity}][{outputs}]({code})".format(
#             arity=self.signature.arity,
#             outputs=self.signature.output_stacks,
#             code=self.code
#         )

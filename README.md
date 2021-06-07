# Poetron

## Description
Poetron is a discord bot that recognizes phrases written in meter and repeats them in poetry format. It currently supports the following meters:
- Iambic pentameter
- Dactylic hexameter
- Hendecasyllabic
- Haikus
- Elegiac couplets
- Trochaic tetrameter
and can easily support any others which can be entirely described as a sequence of stressed and unstressed syllables, with a few that can be either.

## Files
The main bot is contained in _main.py_, while the major functions are contained in _poetrylib.py_. The file _enabled.txt_ allows the user to permanently enable or disable meters if the bot gets too vociferous. For example, the haiku meter can be disabled for a server that already has a haiku bot installed.

## To do:
The python module I have installed to get syllable stresses is not perfect, and I need to modify it so that it is more forgiving.

---

## Bug fix report
- **June 6, 2021**: Prevented spoiler tags from being removed and ignored all messages with single letters that are not A and I.
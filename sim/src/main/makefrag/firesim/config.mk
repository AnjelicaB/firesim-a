# See LICENSE for license details.

# These point at the main class of the target's Chisel generator
DESIGN_PACKAGE ?= firesim.firesim
DESIGN ?= FireSim

# These guide chisel elaboration of the target design specified above.
# See src/main/scala/SimConfigs.scala
TARGET_CONFIG_PACKAGE ?= firesim.firesim
TARGET_CONFIG ?= FireSimRocketConfig

# These guide chisel elaboration of simulation components by MIDAS,
# including models and widgets.
# See src/main/scala/SimConfigs.scala
PLATFORM_CONFIG_PACKAGE ?= firesim.firesim
PLATFORM_CONFIG ?= BaseF1Config

# Override project for the target.
TARGET_SBT_PROJECT := firechip

# Override SBT invokation directory for the target.
TARGET_SBT_DIR := $(chipyard_dir)

# Override SBT/scala sources directory for the target.
TARGET_SOURCE_DIRS := $(chipyard_dir)/generators

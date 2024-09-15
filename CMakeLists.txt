cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

add_compile_definitions(_CPMODULE)

# TODO: document this change
set(CP_C_CONFIGURED DEFINED ENV{CP_ENABLE_NATIVE} OR DEFINED CP_ENABLE_NATIVE)

if (CP_C_CONFIGURED)
python_add_library(
  _C
  MODULE

  src/ccaterpillar/arch.c
  src/ccaterpillar/atomobj.c
  src/ccaterpillar/context.c
  src/ccaterpillar/field.c
  src/ccaterpillar/option.c
  src/ccaterpillar/module.c
  src/ccaterpillar/context.c
  src/ccaterpillar/state.c
  src/ccaterpillar/struct.c
  src/ccaterpillar/layer.c
  src/ccaterpillar/default.c

  src/ccaterpillar/parsing_typeof.c
  src/ccaterpillar/parsing_sizeof.c
  src/ccaterpillar/parsing_pack.c
  src/ccaterpillar/parsing_unpack.c

  src/ccaterpillar/atomimpl/int.c
  src/ccaterpillar/atomimpl/float.c
  src/ccaterpillar/atomimpl/bool.c
  src/ccaterpillar/atomimpl/char.c
  src/ccaterpillar/atomimpl/pad.c
  src/ccaterpillar/atomimpl/string.c
  src/ccaterpillar/atomimpl/const.c
  src/ccaterpillar/atomimpl/bytes.c
  src/ccaterpillar/atomimpl/pstring.c
  src/ccaterpillar/atomimpl/enum.c
  src/ccaterpillar/atomimpl/varint.c
  src/ccaterpillar/atomimpl/computed.c
  src/ccaterpillar/atomimpl/lazy.c
  src/ccaterpillar/atomimpl/cstring.c

  src/ccaterpillar/atomimpl/builtins/builtin.c
  src/ccaterpillar/atomimpl/builtins/repeated.c
  src/ccaterpillar/atomimpl/builtins/condition.c
  src/ccaterpillar/atomimpl/builtins/switch.c
  src/ccaterpillar/atomimpl/builtins/atoffset.c
  src/ccaterpillar/atomimpl/builtins/primitive.c

  WITH_SOABI
)

target_include_directories(_C PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include)

message(STATUS "CMake ${CMAKE_VERSION}")
message(STATUS "Python ${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")

set (CP_GENAPI_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/src/code_gen/genapi.py)
set (CP_CAPI_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillarapi.h.in)
set (CP_CAPI_CSRC ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/caterpillarapi.c.in)
set (CP_CAPI_HEADER_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillarapi.h)
set (CP_CAPI_CSRC_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/caterpillarapi.c)

add_custom_target(
 genapi ALL
 # execute python ./src/code_gen/genapi.py ./src/caterpillar/include/caterpillar/caterpillarapi.h.in ./src/caterpillarapi.c.in
 # in the root directory
 COMMAND ${PYTHON_EXECUTABLE} ${CP_GENAPI_SCRIPT} ${CP_CAPI_HEADER} ${CP_CAPI_CSRC}
 BYPRODUCTS ${CP_CAPI_HEADER_OUT} ${CP_CAPI_CSRC_OUT}
 COMMENT "Generating Public Caterpillar API"
)

add_dependencies(_C genapi)

install(TARGETS _C DESTINATION caterpillar)

else()
MESSAGE(STATUS "Ignoring Caterpillar C extension")
endif()


if(DEFINED ENV{CP_ENABLE_TOOLS})
  # install native extensions for tools (TODO)
else()
MESSAGE(STATUS "Ignoring tools")
endif()

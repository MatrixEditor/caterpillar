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

  src/arch.c
  src/atomobj.c
  src/context.c
  src/field.c
  src/option.c
  src/module.c
  src/context.c
  src/state.c
  src/struct.c
  src/layer.c

  src/parsing_typeof.c
  src/parsing_sizeof.c
  src/parsing_pack.c
  src/parsing_unpack.c

  src/atomimpl/int.c
  src/atomimpl/float.c
  "src/atomimpl/bool.c"
  src/atomimpl/char.c
  src/atomimpl/pad.c
  "src/atomimpl/string.c"
  src/atomimpl/const.c
  src/atomimpl/bytes.c
  src/atomimpl/pstring.c
  src/atomimpl/enum.c
  src/atomimpl/varint.c
  src/atomimpl/computed.c
  src/atomimpl/lazy.c

  src/atomimpl/builtins/builtin.c
  src/atomimpl/builtins/repeated.c
  src/atomimpl/builtins/condition.c
  src/atomimpl/builtins/switch.c
  src/atomimpl/builtins/atoffset.c
  src/atomimpl/builtins/primitive.c

  WITH_SOABI
)

target_include_directories(_C PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include)

message(STATUS "CMake ${CMAKE_VERSION}")
message(STATUS "Python ${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")

set (CP_GENAPI_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/src/code_gen/genapi.py)
set (CP_CAPI_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillarapi.h.in)
set (CP_CAPI_CSRC ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillarapi.c.in)
set (CP_CAPI_HEADER_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillarapi.h)
set (CP_CAPI_CSRC_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillarapi.c)

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

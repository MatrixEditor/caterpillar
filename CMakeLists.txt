cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

add_compile_definitions(_CPMODULE)

# TODO: document this change
if (DEFINED ENV{CP_ENABLE_NATIVE} OR DEFINED CP_ENABLE_NATIVE)
message(STATUS "Building Caterpillar C extension")

python_add_library(
  _C
  MODULE

  src/ccaterpillar/arch.c
  src/ccaterpillar/option.c
  src/ccaterpillar/module.c
  src/ccaterpillar/context.c
  src/ccaterpillar/atom.c
  src/ccaterpillar/lengthinfo.c
  src/ccaterpillar/shared.c
  src/ccaterpillar/atoms/builtin/builtin.c
  src/ccaterpillar/atoms/builtin/repeated.c
  src/ccaterpillar/atoms/builtin/switch.c
  src/ccaterpillar/atoms/builtin/conditional.c
  src/ccaterpillar/atoms/builtin/offset.c

  WITH_SOABI
)

target_include_directories(_C PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include)

message(STATUS "CMake ${CMAKE_VERSION}")
message(STATUS "Python ${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")

set (CP_GENAPI_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/src/code_gen/genapi.py)
set (CP_CAPI_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillarapi.h.in)
set (CP_CAPI_CSRC ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/caterpillarapi.c.in)
set (CP_CAPI_MOD_CSRC ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/module.c.in)
set (CP_CAPI_PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/private.h.in)

set (CP_CAPI_HEADER_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillarapi.h)
set (CP_CAPI_CSRC_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/caterpillarapi.c)
set (CP_CAPI_MOD_CSRC_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/module.c)
set (CP_CAPI_PRIVATE_OUT ${CMAKE_CURRENT_SOURCE_DIR}/src/ccaterpillar/private.h)

add_custom_target(
 genapi ALL
 # execute python ./src/code_gen/genapi.py ./src/caterpillar/include/caterpillar/caterpillarapi.h.in ./src/ccaterpillar/caterpillarapi.c.in
 # in the root directory
 COMMAND ${PYTHON_EXECUTABLE} ${CP_GENAPI_SCRIPT} ${CP_CAPI_HEADER} ${CP_CAPI_CSRC} ${CP_CAPI_MOD_CSRC} ${CP_CAPI_PRIVATE}
 BYPRODUCTS ${CP_CAPI_HEADER_OUT} ${CP_CAPI_CSRC_OUT} ${CP_CAPI_MOD_CSRC_OUT} ${CP_CAPI_PRIVATE_OUT}
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

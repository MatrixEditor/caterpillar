cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)


python_add_library(
  _example
  MODULE

  src/_example.c

  WITH_SOABI
)

# TODO: add command to retrieve caterpillar include dir
target_include_directories(_example PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../src/caterpillar/include)

message(STATUS "CMake ${CMAKE_VERSION}")
message(STATUS "Python ${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")

install(TARGETS _example DESTINATION example)

cmake_minimum_required(VERSION 3.8)

if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

if(CMAKE_BUILD_TYPE MATCHES Debug)
    add_compile_definitions(BUILD_TYPE_DEBUG)
elseif(CMAKE_BUILD_TYPE MATCHES Release)
    add_compile_definitions(BUILD_TYPE_RELEASE)
endif()

project("cpp-app")

find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

file(GLOB_RECURSE SRC_FILES "src/*.cpp" "src/*.h")

add_executable(${PROJECT_NAME} ${PROJECT_NAME}.cpp ${PROJECT_NAME}.h ${SRC_FILES})
target_link_libraries(${PROJECT_NAME} "${TORCH_LIBRARIES}")
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)

if (MSVC)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET ${PROJECT_NAME}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     ${TORCH_DLLS}
                     $<TARGET_FILE_DIR:${PROJECT_NAME}>)
endif (MSVC)

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET cpp-app PROPERTY CXX_STANDARD 20)
endif()
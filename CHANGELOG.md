# Changelog

## [2.6.2] - Patch Release

### Fixed

**caterpillar.field._base**
  - Fix 1-length sized array fields

**caterpillar**
  - Add compatibility with at least Python 3.10 by using `typing_extensions`

## [2.6.1] - Hot-Fix Release

### Fixed

- **caterpillar.fields._base**
  - Fix switch functionality within the `Field` class for `ContextPath` objects

- **caterpillar.fields.common**
  - fix ``%`` operator for the `AsLengthRef` class.

## [2.6.0] - Minor Release

### Added
- **caterpillar.fields._base**
  - Add support for non-context lambda switch fields.

- **caterpillar.fields.common**
  - Add compatibility support for CAPI atoms in `Int`, `UInt` and `PyStructFormattedField`.

- **caterpillar.options**
  - Add custom `Flag.__eq__` implementation to support equality check with `c_Option` objects.

- **caterpillar.abc**
  - Add new typing-only `_OptionLike` protocol.
  - Add missing `_SupportsType` protocol to the stubs file.
  - Add new method `get` to the `_ContextLike` protocol.

- **caterpillar.context**
  - Add new option `O_CONTEXT_FACTORY` that controls the global context type.
    Value must be a method or another type implementing the `_ContextLike` protocol.
  - Add new global context path: `root` (exported as `G` in shortcuts).

- **caterpillar.shortcuts**
  - Add new shortcuts `C` for `ctx`, `P` for `parent` and `G` for the `root` context as `ContextPath` objects.

- **CAPI**
  - New index assignment system when generating CAPI code — a running number is now applied instead of a hard-coded index.
  - Add complete Context implementation in C (`c_Context`) that conforms to the `_ContextLike` protocol.
  - Add `Atom` for C-based struct-like classes (previously known as `catom`).
  - Add native support for `__bits__` in `Atom`.
  - Add special class `LengthInfo` for packing or unpacking multiple objects.
  - New builtin atoms (CAPI): `Repeated`, `Conditional` and `Switch`.
  - Add new shared objects and exception types to the native implementation (`Cp_ContextFactory`, `Cp_ArrayFactory`, `CpExc_Stop` and `Cp_DefaultOption`).

---

### Changed
- **caterpillar.fields._base**
  - Rework `Field` implementation to reduce overhead when packing and unpacking elements.
  - Use pre-computed states instead of calculating everything on the fly; states will be adjusted automatically when setting new values (via `@property` attributes).

---

### Fixed
- **caterpillar.fields.common**
  - Fix issue in `Prefixed` that occurred when the internal struct packs a sequence of elements.

---

### Removed
- **CAPI**
  - Remove old CAPI and completely revamp the CAPI concept to make it compatible with the Python equivalent.


## [2.5.1] - Hot-Fix Release

### Fixed

- **caterpillar.model**
   - An issue when packing or unpacking a bitfield with unnamed fields AND `S_DISCARD_UNNAMED` enabled


## [2.5.0] - Minor Release

### Added
- **caterpillar.abc**
  - Add `_SupportsBits` protocol.
  - Add `_ContainsBits` protocol.
  - Add `_SupportsType` protocol.

- **caterpillar.shortcuts**
  - Add new shortcuts: `typeof`, `to_struct`, `hasstruct`, `getstruct`, and `sizeof`.

- **caterpillar.shared**
  - Add new constants from other modules: `ATTR_BYTEORDER`, `ATTR_TYPE`, `ATTR_BITS`, `ATTR_SIGNED`, `ATTR_TEMPLATE`.

- **caterpillar.context**
  - Add context attribute `_root` to point to the root context instance. Internal parent iteration now uses `self.get(...)`.

---

### Removed
- **caterpillar.abc**
  - Remove `_Action` protocol; split into `_ActionLike = _SupportsActionUnpack | _SupportsActionPack`.
  - Remove `__type__` requirement from `_StructLike`.
  - **Breaking:** Remove `_EnumLike` and `_ContextPathStr`.

- **caterpillar.model**
  - Remove unused `getformat` function.

- **caterpillar.fields.common**
  - Remove unused `__fmt__` function in `Transformer`.

---

### Changed
- **caterpillar.abc**
  - Rename `_Switch` protocol to `_SwitchLike`.
  - Move `STRUCT_FIELD` to `caterpillar.shared` as `ATTR_STRUCT`; move `hasstruct`, `getstruct`, and `typeof` to `caterpillar.shared`.

- **caterpillar.byteorder**
  - Move `BYTEORDER_FIELD` to `caterpillar.shared` as `ATTR_BYTEORDER`.

- **caterpillar.model**
  - Update `sizeof` to check if the object implements `_SupportsSize` protocol.
  - Renew `Bitfield` concept with enhanced syntax.

- **Documentation**
  - Update reference and library docs; improve section numbering.

---

### Fixed
- **caterpillar.model**
  - Fix parsing of union objects with an unbound stream.
  - Fix field options in Sequences and Structs not being populated when creating fields.

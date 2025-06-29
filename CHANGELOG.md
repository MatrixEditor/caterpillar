# Changelog

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

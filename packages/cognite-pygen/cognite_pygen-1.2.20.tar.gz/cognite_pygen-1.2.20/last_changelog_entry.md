
### Fixed

- When calling `.as_write()` on class with direct relations to a
'parent' view. The view type is maintained. For example, if I have a
data model with `MyAsset` view that implements `CogniteAsset`, and I
have a `MyFile` view that has a direct relation property named `asset`
with type `CogniteAsset`. Then, if I have an instance of `MyFile` with
the asset property set to an instance of `MyAsset`, then after calling
`.as_write()` on `MyFile` I will now have a `MyFileWrite` instances
which has the `asset` property set to an instance of `MyAssetWrite`
instead of `CogniteAssetWrite`.
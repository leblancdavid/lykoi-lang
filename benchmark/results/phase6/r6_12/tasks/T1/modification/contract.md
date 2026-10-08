# T1 staged change — Resize active holds

1. Retain every base obligation and original request/observation. Extend the
   operation union with exactly `{kind:"resize",id,n}`; id uses the base ID
   syntax and n is an integer 1–100. Whole-request shape validation includes it.
2. At its operation index, reject a nonactive ID with `unknown_hold`. Otherwise
   let d=n−old_n. If d>free for that hold's SKU, return `insufficient`. Otherwise
   set free=free−d, held=held+d and hold.n=n. A decrease returns units; equality
   is a successful no-op. Shipped units and the used-ID set do not change.
3. All base bounds, error shapes, ordering and environment rules remain in force.

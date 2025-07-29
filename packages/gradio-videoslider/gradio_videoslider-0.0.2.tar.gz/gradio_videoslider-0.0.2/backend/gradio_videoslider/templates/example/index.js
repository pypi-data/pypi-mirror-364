const {
  SvelteComponent: k,
  append_hydration: d,
  attr: c,
  children: w,
  claim_element: g,
  claim_space: y,
  detach: o,
  element: v,
  init: E,
  insert_hydration: I,
  noop: p,
  safe_not_equal: q,
  space: b,
  src_url_equal: h,
  toggle_class: f
} = window.__gradio__svelte__internal;
function G(r) {
  let e, s, n, u, i, _, a, m;
  return {
    c() {
      e = v("div"), s = v("img"), u = b(), i = v("img"), a = b(), m = v("span"), this.h();
    },
    l(t) {
      e = g(t, "DIV", { class: !0 });
      var l = w(e);
      s = g(l, "IMG", { src: !0, class: !0 }), u = y(l), i = g(l, "IMG", { src: !0, class: !0 }), a = y(l), m = g(l, "SPAN", { class: !0 }), w(m).forEach(o), l.forEach(o), this.h();
    },
    h() {
      h(s.src, n = /*samples_dir*/
      r[1] + /*value*/
      r[0][0]) || c(s, "src", n), c(s, "class", "svelte-l4wpk0"), h(i.src, _ = /*samples_dir*/
      r[1] + /*value*/
      r[0][1]) || c(i, "src", _), c(i, "class", "svelte-l4wpk0"), c(m, "class", "svelte-l4wpk0"), c(e, "class", "wrap svelte-l4wpk0"), f(
        e,
        "table",
        /*type*/
        r[2] === "table"
      ), f(
        e,
        "gallery",
        /*type*/
        r[2] === "gallery"
      ), f(
        e,
        "selected",
        /*selected*/
        r[3]
      );
    },
    m(t, l) {
      I(t, e, l), d(e, s), d(e, u), d(e, i), d(e, a), d(e, m);
    },
    p(t, [l]) {
      l & /*samples_dir, value*/
      3 && !h(s.src, n = /*samples_dir*/
      t[1] + /*value*/
      t[0][0]) && c(s, "src", n), l & /*samples_dir, value*/
      3 && !h(i.src, _ = /*samples_dir*/
      t[1] + /*value*/
      t[0][1]) && c(i, "src", _), l & /*type*/
      4 && f(
        e,
        "table",
        /*type*/
        t[2] === "table"
      ), l & /*type*/
      4 && f(
        e,
        "gallery",
        /*type*/
        t[2] === "gallery"
      ), l & /*selected*/
      8 && f(
        e,
        "selected",
        /*selected*/
        t[3]
      );
    },
    i: p,
    o: p,
    d(t) {
      t && o(e);
    }
  };
}
function M(r, e, s) {
  let { value: n } = e, { samples_dir: u } = e, { type: i } = e, { selected: _ = !1 } = e;
  return r.$$set = (a) => {
    "value" in a && s(0, n = a.value), "samples_dir" in a && s(1, u = a.samples_dir), "type" in a && s(2, i = a.type), "selected" in a && s(3, _ = a.selected);
  }, [n, u, i, _];
}
class S extends k {
  constructor(e) {
    super(), E(this, e, M, G, q, {
      value: 0,
      samples_dir: 1,
      type: 2,
      selected: 3
    });
  }
}
export {
  S as default
};

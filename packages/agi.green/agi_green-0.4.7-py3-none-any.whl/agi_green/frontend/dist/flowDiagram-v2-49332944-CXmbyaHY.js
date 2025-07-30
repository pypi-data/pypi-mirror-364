import { p as a, f as o } from "./flowDb-d35e309a-Ce4vx_zF.js";
import { f as e, g as t } from "./styles-7383a064-COfXmP_W.js";
import { t as s } from "./main-CNm7E6Fw.js";
import "./graph-3beSvB20.js";
import "./layout-COXLQBkE.js";
const p = {
  parser: a,
  db: o,
  renderer: e,
  styles: t,
  init: (r) => {
    r.flowchart || (r.flowchart = {}), r.flowchart.arrowMarkerAbsolute = r.arrowMarkerAbsolute, s({ flowchart: { arrowMarkerAbsolute: r.arrowMarkerAbsolute } }), e.setConf(r.flowchart), o.clear(), o.setGen("gen-2");
  }
};
export {
  p as diagram
};
//# sourceMappingURL=flowDiagram-v2-49332944-CXmbyaHY.js.map

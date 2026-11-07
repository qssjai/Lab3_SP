import json

def node_to_dictionary(node):
    children_as_dictionaries = []
    for child_node in node.children:
        children_as_dictionaries.append(node_to_dictionary(child_node))

    return {
        "name": node.node_type,
        "value": node.value,           
        "children": children_as_dictionaries,
    }

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<title>AST — дерево розбору програми</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
  body { margin: 0; font-family: Arial, sans-serif; background: #f7f7fb; }
  header { height: 56px; box-sizing: border-box; padding: 8px 20px; background: #2b2d42;
           color: white; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
  header h1 { font-size: 18px; margin: 0; }
  header .hint { font-size: 12px; opacity: 0.75; }
  #legend { display: flex; gap: 14px; font-size: 12px; }
  #legend span { display: inline-flex; align-items: center; gap: 5px; }
  #legend i { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
  svg { width: 100vw; height: calc(100vh - 56px); display: block; }
  .link { fill: none; stroke: #b8b8c8; stroke-width: 1.5px; }
  .node circle { stroke: #2b2d42; stroke-width: 1.5px; cursor: pointer; }
  .node text { font-size: 13px; fill: #222; text-anchor: middle;
               paint-order: stroke; stroke: #f7f7fb; stroke-width: 4px; }
  #error { padding: 20px; color: #b00020; }
</style>
</head>
<body>
<header>
  <h1>Дерево розбору (AST)</h1>
  <div id="legend"></div>
  <div class="hint">Колесо миші — масштаб · перетягування — рух · клік по вузлу — згорнути/розгорнути</div>
</header>
<div id="error"></div>
<svg id="tree"></svg>

<script>
if (typeof d3 === "undefined") {
  document.getElementById("error").textContent =
    "Не вдалося завантажити d3.js. Для відображення дерева потрібне підключення до інтернету.";
} else {

  const treeData = __TREE_DATA__;

  const colorByNodeType = {
    "Program": "#2b2d42",
    "Declaration": "#ef8354", "Assignment": "#ef8354", "Print": "#ef8354",
    "If": "#ef8354", "While": "#ef8354",
    "Block": "#bfc0c0",
    "BinaryOperation": "#4f9da6", "UnaryMinus": "#4f9da6",
    "Number": "#8ac926", "Variable": "#ffca3a"
  };

  const legendItems = [
    ["#2b2d42", "програма"], ["#ef8354", "інструкція"], ["#bfc0c0", "блок"],
    ["#4f9da6", "операція"], ["#8ac926", "число"], ["#ffca3a", "змінна"]
  ];
  legendItems.forEach(function (item) {
    const legendEntry = d3.select("#legend").append("span");
    legendEntry.append("i").style("background", item[0]);
    legendEntry.append("text").text(item[1]);
  });

  const svg = d3.select("#tree");
  const zoomLayer = svg.append("g");
  const linkLayer = zoomLayer.append("g");   // шар для ліній між вузлами
  const nodeLayer = zoomLayer.append("g");   // шар для самих вузлів (зверху)

  const zoomBehavior = d3.zoom()
    .scaleExtent([0.05, 3])
    .on("zoom", function (event) { zoomLayer.attr("transform", event.transform); });
  svg.call(zoomBehavior);

  const rootNode = d3.hierarchy(treeData);
  let nextNodeId = 0;
  rootNode.descendants().forEach(function (node) { node.id = nextNodeId++; });

  const treeLayout = d3.tree().nodeSize([40, 220]);
  const linkGenerator = d3.linkHorizontal()
    .x(function (node) { return node.y; })
    .y(function (node) { return node.x; });

  function labelOf(node) {
    const value = node.data.value;
    if (value === null || value === undefined) { return node.data.name; }
    return node.data.name + " (" + value + ")";
  }

  function toggleChildren(event, node) {
    if (node.children) {
      node._children = node.children;
      node.children = null;
    } else {
      node.children = node._children;
      node._children = null;
    }
    update();
  }
  
  function update() {
    treeLayout(rootNode);

    linkLayer.selectAll(".link")
      .data(rootNode.links(), function (link) { return link.target.id; })
      .join("path")
      .attr("class", "link")
      .attr("d", linkGenerator);

    const nodeGroups = nodeLayer.selectAll(".node")
      .data(rootNode.descendants(), function (node) { return node.id; })
      .join(function (enterSelection) {
        const newGroups = enterSelection.append("g")
          .attr("class", "node")
          .on("click", toggleChildren);
        newGroups.append("circle").attr("r", 9);
        newGroups.append("text").attr("dy", "-14");
        return newGroups;
      })
      .attr("transform", function (node) { return "translate(" + node.y + "," + node.x + ")"; });

    nodeGroups.select("circle")
      .attr("fill", function (node) { return colorByNodeType[node.data.name] || "#cccccc"; })
      .attr("stroke-dasharray", function (node) { return node._children ? "3,2" : null; });

    nodeGroups.select("text").text(labelOf);
  }

  function fitTreeToScreen() {
    const allNodes = rootNode.descendants();
    const topX = d3.min(allNodes, function (node) { return node.x; });
    const bottomX = d3.max(allNodes, function (node) { return node.x; });
    const rightY = d3.max(allNodes, function (node) { return node.y; });

    const viewWidth = window.innerWidth;
    const viewHeight = window.innerHeight - 56;
    const treeHeight = bottomX - topX + 100;
    const treeWidth = rightY + 300;
    const scale = Math.min(1, viewHeight / treeHeight, viewWidth / treeWidth);
    const shiftY = viewHeight / 2 - scale * (topX + bottomX) / 2;

    svg.call(zoomBehavior.transform, d3.zoomIdentity.translate(40, shiftY).scale(scale));
  }

  update();
  fitTreeToScreen();
}
</script>
</body>
</html>
"""

def create_tree_html(syntax_tree, output_file_name):
    """Зберігає HTML-сторінку з малюнком дерева у файл output_file_name."""
    tree_dictionary = node_to_dictionary(syntax_tree)
    tree_json_text = json.dumps(tree_dictionary, ensure_ascii=False)

    # замінюємо заглушку в шаблоні на справжні дані дерева
    html_text = HTML_TEMPLATE.replace("__TREE_DATA__", tree_json_text)

    with open(output_file_name, "w", encoding="utf-8") as output_file:
        output_file.write(html_text)

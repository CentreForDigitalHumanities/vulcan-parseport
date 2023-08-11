const NODE_CLASSNAME = "node"
const GRAPH_LABEL_MARGIN = 20

const SHADOW_OVERSIZE = 2

const ALL_NODES = []

class Node {
    constructor(node_position, group, rectangle, content, color, shadow) {
        this.position = node_position[0]
        this.group = group
        this.rectangle = rectangle
        this.content = content
        this.color = color
        this.rectangle.attr("stroke", color)
        this.shadow = shadow
        this.registeredEdges = []
    }

    translate(x, y) {
        // this.group.attr("transform", "translate(" + x + "," + y + ")")
        this.position.x = x
        this.position.y = y
        this.group.attr("transform", "translate(" + this.position.x + "," + this.position.y + ")")
    }

    getWidth() {
        return this.content.getWidth()
    }

    setWidth(width) {
        this.rectangle.attr("width", width)
        this.content.recenter(width)
        if (this.shadow != null) {
            this.shadow.attr("width", width + 2*SHADOW_OVERSIZE)
        }
    }

    static get_hypothetical_node_width(node_label) {
        return node_label.length*6.5 + 22
    }

    getHeight() {
        return this.content.getHeight()
    }

    getX() {
        return this.position.x
    }

    getY() {
        return this.position.y
    }

    registerGraphEdge(edge, edge_label, edge_position_data, graph) {
        this.registeredEdges.push([edge, edge_label, edge_position_data, graph])
    }

    registerDependencyEdge(edge, is_outgoing, label, table) {
        this.registeredEdges.push([edge, is_outgoing, label, table])
    }

}

function create_and_register_node_object(node_position, node_group, rect, content_object, color,
                                         shadow=null) {
    let node_object = new Node(node_position, node_group, rect, content_object, color, shadow)

    ALL_NODES.push(node_object)

    return node_object;
}

function getNodePosition(x, y) {
    return [{x: x, y: y, id: ALL_NODES.length}];
}

function makeNodeGroup(canvas, node_position, classname) {
    return canvas.data(node_position).append("g")
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        .attr("class", classname);
}

function makeNodeRectangle(is_bold, do_highlight, node_group, content_object, classname) {
    let stroke_width = is_bold ? "4" : "2"

    let fill = "white"
    if (do_highlight) {
        fill = "#56e37c"
    }

    return node_group.append("rect")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", content_object.getWidth())
        .attr("height", content_object.getHeight())
        .attr("fill", fill)
        .attr("stroke-width", stroke_width)
        .attr("class", classname)
        .lower();
}

function makeCellRectangle(is_bold, do_highlight, node_group, content_object, classname) {
    if (is_bold) {
        console.log("Warning: Cell was marked as bold, but this is currently not possible.")
    }

    let stroke_width = "0"

    let fill = "white"
    if (do_highlight) {
        fill = "#56e37c"
    }

    return node_group.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", content_object.getWidth())
        .attr("height", content_object.getHeight())
        .attr("fill", fill)
        .attr("stroke-width", stroke_width)
        .attr("class", classname)
        .lower();
}

function makeCellShadow(node_group, content_object, classname) {

    return node_group.append("rect")
        .attr("x", -SHADOW_OVERSIZE)
        .attr("y", -SHADOW_OVERSIZE)
        .attr("width", content_object.getWidth() + 2 * SHADOW_OVERSIZE)
        .attr("height", content_object.getHeight() + 2 * SHADOW_OVERSIZE)
        .attr("fill", "#cccccc")
        .attr("stroke-width", "0")
        .attr("class", classname)
        // blur
        .attr("filter", "url(#white-border-inset)")
        .lower();
}


function createNode(x, y, content_data, content_type, canvas, is_bold, do_highlight,
                    drag_function=null, classname=NODE_CLASSNAME) {

    return createNodeWithColor(x, y, content_data, content_type, canvas, is_bold, do_highlight, "black",
                    drag_function, classname);

}

function createNodeWithColor(x, y, content_data, content_type, canvas, is_bold, do_highlight, color,
                    drag_function, classname=NODE_CLASSNAME) {

    let node_position = getNodePosition(x, y);

    let node_group = makeNodeGroup(canvas, node_position, classname)

    let content_object = createNodeContent(content_data, content_type, node_group, classname)

    let rect = makeNodeRectangle(is_bold, do_highlight, node_group, content_object, classname);

    if (drag_function != null) {
        let nodeDragHandler = d3.drag().on('drag', drag_function);
        nodeDragHandler(node_group);
    }

    return create_and_register_node_object(node_position, node_group, rect, content_object, color);

}

function createCell(x, y, content_data, content_type, canvas, is_bold, do_highlight, classname=NODE_CLASSNAME) {

    let node_position = getNodePosition(x, y);

    let node_group = makeNodeGroup(canvas, node_position, classname)

    let content_object = createNodeContent(content_data, content_type, node_group, classname)

    let rect = makeCellRectangle(is_bold, do_highlight, node_group, content_object, classname)

    let shadow = makeCellShadow(node_group, content_object, classname)

    return create_and_register_node_object(node_position, node_group, rect, content_object, "black",
        shadow)

}




function createNodeContent(content_data, content_type, append_to_this_object, classname) {

    if (content_type == "STRING") {
        if (content_data == null) {
            content_data = ""
        }
        let rect_width = Node.get_hypothetical_node_width(content_data);
        let rect_height = 30;
        let text_object = append_to_this_object.append("text")
            .attr("text-anchor", "middle")
            .attr("x", rect_width/2)
            .attr("y", rect_height/2)
            .attr("dy", ".3em")
            .style("pointer-events", "none")
            .attr("class", classname)
            .text(content_data)
        return new NodeStringContent(text_object, rect_width, rect_height)
    } else if (content_type == "GRAPH" || content_type == "TREE") {
        return new Graph(0, 0, content_data, append_to_this_object, false,
            GRAPH_LABEL_MARGIN)
    }

}

class NodeStringContent {
    constructor(text_object, width, height) {
        this.text_object = text_object
        this.width = width
        this.height = height
    }

    recenter(new_width) {
        this.width = new_width
        this.text_object.attr("x", new_width/2)
    }

    getWidth() {
        return this.width
    }

    getHeight() {
        return this.height
    }
}

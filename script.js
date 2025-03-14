// Lataa JSON-data Finlexistä
fetch("finlex_data.json")
    .then(response => response.json())
    .then(data => {
        drawTree(data);  // Piirretään puu
    })
    .catch(error => console.error("Virhe haettaessa dataa:", error));

// Piirretään puu D3.js:llä
function drawTree(treeData) {
    const width = 1000, height = 600;
    const svg = d3.select("body")
                  .append("svg")
                  .attr("width", width)
                  .attr("height", height)
                  .append("g")
                  .attr("transform", "translate(50,50)");

    const treeLayout = d3.tree().size([width - 100, height - 100]);
    const root = d3.hierarchy(treeData);
    treeLayout(root);

    // Piirretään viivat
    svg.selectAll(".link")
       .data(root.links())
       .enter()
       .append("line")
       .attr("class", "link")
       .attr("x1", d => d.source.x)
       .attr("y1", d => d.source.y)
       .attr("x2", d => d.target.x)
       .attr("y2", d => d.target.y)
       .attr("stroke", "black");

    // Piirretään solmut
    svg.selectAll(".node")
       .data(root.descendants())
       .enter()
       .append("circle")
       .attr("class", "node")
       .attr("cx", d => d.x)
       .attr("cy", d => d.y)
       .attr("r", 6)
       .attr("fill", "steelblue");

    // Piirretään tekstit
    svg.selectAll(".text")
       .data(root.descendants())
       .enter()
       .append("text")
       .attr("x", d => d.x + 10)
       .attr("y", d => d.y + 5)
       .text(d => d.data.name);
}

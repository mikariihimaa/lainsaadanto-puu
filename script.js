// Filex API:n URL (vaihda oikea Filexin avoimen datan osoite)
const FILEX_API_URL = "https://api.avoin.lainsaadanto.fi/filex"; 

// Hakee Filexin JSON-datan
fetch(FILEX_API_URL)
    .then(response => response.json())
    .then(data => {
        const root = convertToHierarchy(data); // Muunnetaan data puumuotoon
        drawTree(root); // Piirretään puu
    })
    .catch(error => console.error("Virhe haettaessa dataa:", error));

// Muuntaa Filex-datan puumuotoiseksi
function convertToHierarchy(data) {
    let root = { name: "Lainsäädäntö", children: [] };
    data.lait.forEach(laki => {
        let lakiNode = { name: laki.nimi, children: [] };
        laki.asetukset.forEach(asetus => {
            lakiNode.children.push({ name: asetus.nimi });
        });
        root.children.push(lakiNode);
    });
    return root;
}

// Piirtää puun D3.js:llä
function drawTree(treeData) {
    const width = window.innerWidth, height = 600;
    const svg = d3.select("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", "translate(50,50)");

    const treeLayout = d3.tree().size([width - 100, height - 100]);
    const root = d3.hierarchy(treeData);
    treeLayout(root);

    // Piirretään linkit
    g.selectAll(".link")
        .data(root.links())
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    // Piirretään solmut
    g.selectAll(".node")
        .data(root.descendants())
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("r", 6)
        .on("click", d => alert(d.data.name)); // Klikkaus näyttää lain nimen

    // Piirretään tekstit
    g.selectAll(".text")
        .data(root.descendants())
        .enter()
        .append("text")
        .attr("x", d => d.x + 10)
        .attr("y", d => d.y + 5)
        .text(d => d.data.name);
}

"use strict";

async function scan(file) {
    const form = new FormData();
    form.append("file", file);

    try {
        const response = await fetch("/scan", {
            method: "POST",
            body: form
        });
        return await response.json();
    } catch (error) {
        console.error(error);
        return {};
    }
}

window.addEventListener("DOMContentLoaded", function() {
    var app = new Vue({
        el: "#dropzone",
        data: {
            dragActive: false,
            analyzing: false,
            filename: "",
            results: {}
        },
        methods: {
            drop: async function(event) {
                this.dragActive = false;

                const items = event.dataTransfer.items;
                if (items.length >= 1 && items[0].kind == "file") {
                    var file = items[0].getAsFile();
                    this.analyzing = true;
                    this.filename = file.name;
                    const results = await scan(file);
                    this.analyzing = false;
                    this.results = results;
                }
            },
            dragOver: function(event) {
                this.dragActive = true;
            },
            dragLeave: function(event) {
                this.dragActive = false;
            }
        }
    });
});

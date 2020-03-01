$('.stock-formset').formset({
    addText: "Добавить позицию",
    deleteText: "Удалить",
    deleteCssClass: "deletelink",
    addCssClass: "addlink",
    added: (row) => {row.find('input[type="number"]').val("1")}
});

$(document).ready(function(){
    $('.order-formset').formset({
        addText: "Добавить позицию",
        deleteText: "Удалить",
        deleteCssClass: "deletelink",
        addCssClass: "addlink",
        added: (row) => {row.find('input[type="number"]').val("1")}
    });

    $('#id_reg').click(function(){
        if ($(this).is(':checked')){
            $('#sel_cus').show();
            $('#reg_cus').hide();
            $('#id_customer').removeAttr('disabled');
            $('#id_full_name').attr('disabled', 'disabled');
            $('#id_phone_number').attr('disabled', 'disabled');
            $('#id_email').attr('disabled', 'disabled');
            $('#id_contact_info').attr('disabled', 'disabled');
        } else {
            $('#sel_cus').hide();
            $('#reg_cus').show();
            $('#id_customer').attr('disabled', 'disabled');
            $('#id_full_name').removeAttr('disabled');
            $('#id_phone_number').removeAttr('disabled');
            $('#id_email').removeAttr('disabled');
            $('#id_contact_info').removeAttr('disabled');
        }
     });

    $('fieldset').on('change', '.category', function () {
        var item = $(this).next();
        item.empty();
        $.getJSON(location.href, {'category': $(this).val()})
            .done(function (data) {
                item.prepend('<option value="">---------</option>');
                $.each(data, function(pk, value) {
                    item.append('<option value="' + pk + '">' + value + '</option>');
            });
        })
    })

})
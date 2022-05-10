$(".checkAll").on('change',function(){
    $(".checkbox").prop('checked',$(this).is(":checked"));
    });
$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.product_id);
        $("#condition").val(res.condition)
        $("#name").val(res.name);
        $("#quantity").val(res.quantity);
        $("#reorder_quantity").val(res.reorder_quantity);
        $("#restock_level").val(res.restock_level);
        
        if (res.active == true) {
            $("#active").val("true");
        } else {
            $("#active").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#condition").val("");
        $("#name").val("");
        $("#quantity").val("");
        $("#reorder_quantity").val("");
        $("#restock_level").val("");
        $("#active").val("");
        $("#ordered_quantity").val("")
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        let product_id = parseInt($("#product_id").val());
        let condition = $("#condition").val();
        let name = $("#name").val();
        let quantity = parseInt($("#quantity").val());
        let reorder_quantity = parseInt($("#reorder_quantity").val());
        let restock_level = parseInt($("#restock_level").val());
        let active = $("#active").val() == "true";

        let data = {
            "product_id": product_id,
            "condition": condition,
            "name": name,
            "quantity": quantity,
            "reorder_quantity": reorder_quantity,
            "restock_level": restock_level,
            "active": active,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/inventory`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        let product_id = parseInt($("#product_id").val());
        let condition = $("#condition").val();
        condition = condition.toUpperCase();
        let name = $("#name").val();
        let quantity = parseInt($("#quantity").val());
        let reorder_quantity = parseInt($("#reorder_quantity").val());
        let restock_level = parseInt($("#restock_level").val());
        let active = $("#active").val() == "true";

        let data = {
            "product_id": product_id,
            "name": name,
            "quantity": quantity,
            "reorder_quantity": reorder_quantity,
            "restock_level": restock_level,
            "active": active,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/inventory/${product_id}/${condition}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Read/Retrieve a Product
    // ****************************************

    $("#read-btn").click(function () {

        let product_id = parseInt($("#product_id").val());
        let condition = $("#condition").val();
        condition = condition.toUpperCase();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/${product_id}/${condition}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        let product_id = parseInt($("#product_id").val());
        let condition = $("#condition").val();
        condition = condition.toUpperCase();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventory/${product_id}/${condition}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Checkout a Product
    // ****************************************

    $("#checkout-btn").click(function() {
        let product_id = parseInt($("#product_id").val());
        let condition = $("#condition").val();
        condition = condition.toUpperCase();
        let ordered_quantity = parseInt($("#ordered_quantity").val());

        let data = {
            "ordered_quantity": ordered_quantity
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/inventory/checkout/${product_id}/${condition}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been checked out from Inventory!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Reorder a Product
    // ****************************************

    $("#reorder-btn").click(function() {
        let product_id = parseInt($("#product_id").val());
        let condition = $("#condition").val();
        condition = condition.toUpperCase();
        let ordered_quantity = parseInt($("#ordered_quantity").val());

        let data = {
            "ordered_quantity": ordered_quantity
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/inventory/reorder/${product_id}/${condition}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been reordered!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    // $("#search-btn").click(function () {

    //     let name = $("#pet_name").val();
    //     let category = $("#pet_category").val();
    //     let available = $("#pet_available").val() == "true";

    //     let queryString = ""

    //     if (name) {
    //         queryString += 'name=' + name
    //     }
    //     if (category) {
    //         if (queryString.length > 0) {
    //             queryString += '&category=' + category
    //         } else {
    //             queryString += 'category=' + category
    //         }
    //     }
    //     if (available) {
    //         if (queryString.length > 0) {
    //             queryString += '&available=' + available
    //         } else {
    //             queryString += 'available=' + available
    //         }
    //     }

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //         type: "GET",
    //         url: `/pets?${queryString}`,
    //         contentType: "application/json",
    //         data: ''
    //     })

    //     ajax.done(function(res){
    //         //alert(res.toSource())
    //         $("#search_results").empty();
    //         let table = '<table class="table table-striped" cellpadding="10">'
    //         table += '<thead><tr>'
    //         table += '<th class="col-md-2">ID</th>'
    //         table += '<th class="col-md-2">Name</th>'
    //         table += '<th class="col-md-2">Category</th>'
    //         table += '<th class="col-md-2">Available</th>'
    //         table += '<th class="col-md-2">Gender</th>'
    //         table += '<th class="col-md-2">Birthday</th>'
    //         table += '</tr></thead><tbody>'
    //         let firstPet = "";
    //         for(let i = 0; i < res.length; i++) {
    //             let pet = res[i];
    //             table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.category}</td><td>${pet.available}</td><td>${pet.gender}</td><td>${pet.birthday}</td></tr>`;
    //             if (i == 0) {
    //                 firstPet = pet;
    //             }
    //         }
    //         table += '</tbody></table>';
    //         $("#search_results").append(table);

    //         // copy the first result to the form
    //         if (firstPet != "") {
    //             update_form_data(firstPet)
    //         }

    //         flash_message("Success")
    //     });

    //     ajax.fail(function(res){
    //         flash_message(res.responseJSON.message)
    //     });

    // });

    

})
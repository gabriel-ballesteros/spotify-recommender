
$(document).ready(function () {
    var api_url = "http://127.0.0.1:5000/recommender/api/v1.0";
    $("#search-button").click(function () {
        if (document.getElementById("search-text").value) {
            $("#search-button").empty();
            $("#search-button").addClass("disabled");
            $("#search-button").append(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    Loading...`);
            $("#search-table").empty();
            $.get(`${api_url}/search=${document.getElementById("search-text").value}`, function (data) {
                $("#search-table").empty();
                data.forEach(async element => {
                    $("#search-table").append($(
                        `<tr>
                    <td>${element.name}</td>
                    <td>${element["artists"].map(e => e.name).join(", ")}</td>
                    <td>${element.album.name}</td>
                    <td>${element.album.release_date.substr(0, 4)}</td>
                    <td><button track_id="${element.id}"
                    type="button" class="btn btn-primary btn-small table-button add-button" style="width: 50%;">
                    <svg class="bi" width="20" height="20" fill="currentColor" style="position: relative; left: 0.2em; bottom: 0.1em;">
                    <use xlink:href="static/icons/bootstrap-icons.svg#plus-square-fill" />
                        </svg></button></td>
                </tr>`
                    ).hide().fadeIn(500));

                });
                $("#search-button").empty();
                $("#search-button").append("Search");
                $("#search-button").removeClass("disabled");
            });
        }
    });

    $(document).on('click', '.add-button', function (event) {
        if ($(`[track_id='${$(event.target).attr('track_id')}']`).length < 2) {
            $("#list-table").append($(`
            <tr>
            <td>${$(this).parent().parent().children().eq(0).text()}</td>
            <td class="artist-name">${$(this).parent().parent().children().eq(1).text()}</td>
            <td>${$(this).parent().parent().children().eq(2).text()}</td>
            <td>${$(this).parent().parent().children().eq(3).text()}</td>
            <td class="d-grid gap-2"><button track_id="${$(this).attr("track_id")}"
            type="button" class="btn btn-danger btn-block table-button remove-button" style="width: 50%;">
            <svg class="bi" width="20" height="20" fill="currentColor" style="position: relative; left: 0.2em; bottom: 0.1em;">
            <use xlink:href="static/icons/bootstrap-icons.svg#dash-square-fill" />
            </svg></button></td>
            </tr>`).hide().fadeIn(500));
        }
        //else {
        //   error agregar mas de una del mismo id
        //}
    });

    $(document).on('click', '.remove-button', function () {
        $($(this)).parent().parent().fadeOut(500, function () {
            $($(this)).remove();
        });
    });

    $(document).on('click', '#empty-button', function () {
        $("#list-table").fadeOut(500, function () {
            $("#list-table").empty();

        });
    });

    $(document).on('click', '#submit-button', function () {
        if (Array.from($('.remove-button')).length > 0) {
            var ids = Array.from($('.remove-button').map(function () {
                return $(this).attr('track_id');
            }));
            var artists_in_list = [0];
            if ($("#listedArtists").is(":checked")) {
                artists_in_list = Array.from($('.artist-name').map(function () {
                    return $(this).text();
                }));
            }
            $("#input_div").fadeOut(500);
            $("#spinner_search").fadeIn(500);
            $.get(`${api_url}/recommendations=${$("#fromYear").text()}&${$("#toYear").text()}&${artists_in_list.join()}&${+ $("#popularArtists").is(":checked")}&${+ $("#explicit").is(":checked")}&${ids.join(";")}`, function (data) {
                $("#spinner_search").hide();
                $("#recommendations_div").fadeIn(500);
                data.forEach(element => {
                    var match_color = "limegreen";
                    if (element.match <= 20) {
                        match_color = "firebrick";
                    }
                    else if (element.match <= 80) {
                        match_color = "yellow";
                    }
                    $("#recommendations_table").append($(`
                <tr>
                <td>${element.name}</td>
                <td>${element.artist}</td>
                <td>${element.album}</td>
                <td>${element.year}</td>
                <td class="d-grid gap-2"><img class="img-fluid rounded"
                    src="${element.img}">
                  <div class="progress position-relative">
                    <div class="progress-bar" role="progressbar" style="width: ${element.match}%; background-color: ${match_color};"
                      aria-valuenow="${element.match}" aria-valuemin="0" aria-valuemax="100"></div>
                    <span class="justify-content-center d-flex position-absolute w-100">${element.match}% match</span>
                  </div>
                  <a class="btn btn-success btn-block spotify" href="${element.uri}" target="_blank">Listen on <img class="img-fluid" width="20px"
                      style="position:relative; left: 0.5em;" src="static/img/Spotify_Icon_RGB_White.png"></a>
                </td>
              </tr>`).hide().fadeIn(500));
                });
            });
        }
    });

    $(document).on('click', '#go_back_button', function () {
        $("#recommendations_div").fadeOut(500, function () {
            $("#search-table").empty();
            $("#list-table").empty();
            $("#recommendations_table").empty();
            $("#search-text").val("");
            $("#input_div").fadeIn(500);
        });
    });
});
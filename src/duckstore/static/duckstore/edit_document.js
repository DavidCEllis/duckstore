$('html').addClass('hidden')

function clearForm() {
  let date = new Date().toISOString().slice(0, 10)
  $('#docform')[0].reset()
  $('#date_added').val(date)
}

function fillForm(data) {
  $('#date_added').val(data['date_added'])
  $('#ID').val(data['id'])
  $('#title').val(data['title'])
  $('#date_received').val(data['date_received'])
  $('#location').val(data['location'])

  let tag_ids = data['tags'].map(tag => tag['name'])
  $('#tags').val(tag_ids).trigger('change')
  let source_ids = data['sources'].map(source => source['name'])
  $('#sources').val(source_ids).trigger('change')

  let files = data['files']
  if (files.length > 0) {
    let filelist = document.getElementById("filelist")
    let new_html = ""
    for (let file of files) {
        new_html += `
            <div class='row'><div class='col-lg'>
              <a href="download?file_id=${file['id']}">${file["original_name"]}</a>
            </div></div>
        `
    }
    filelist.innerHTML = new_html
    $("#filelist_parent").removeClass("hidden")
  }

}

function getDoc(docid) {
  $.post(
    '/docdata',
    {'docid': docid},
    function (doc, status) {
      if (status === 'success') {
        fillForm(doc)
      } else {
        window.alert("Could not fetch document data from server: " + status)
      }
    }
  )
}

$(document).ready(function () {
  // I couldn't figure out where the newlines were being added to the text
  // Of all the options so here just remove them?
  // This is kind of a hack until I can figure this out
  let selectors = $('select')

  selectors.each(function () {
    for (let option of this.options) {
      option.innerHTML = option.innerHTML.trim()
    }
  })


  selectors.select2({
    theme: 'bootstrap4',
    tags: true,
    tokenSeparators: [','],
    // selectOnClose: true,
    createTag: function (params) {
      let term = $.trim(params.term)
      if (term === '') { return null }
      return {
        id: term,
        text: term
      }
    },
    insertTag: function (data, tag) {
      data.push(tag);
    }
  })

  $('#tags').append(new Option("TEST", "TEST"))

  $('#date_added').prop('disabled', true)  // Lazy disabling of date added manually
  $('#files').prop('class', 'form-control-file')
  $('html').removeClass('hidden')
})

$('html').addClass('hidden')

$(document).ready(function () {
  $('#source').select2()
  $('#tags').select2()
  $('select').select2({ theme: 'bootstrap4' })
  $('html').removeClass('hidden')
})

const _filepath = filepath
const _filecontent = filecontent
const blob = new Blob([_filecontent])

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, _filepath)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = _filepath
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}


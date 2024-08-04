// Загрузка YouTube IFrame API
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var youtubePlayer;

// Функция вызывается, когда YouTube IFrame API готов
function onYouTubeIframeAPIReady() {
    youtubePlayer = new YT.Player('youtube-video', {
        events: {
            'onStateChange': onPlayerStateChange
        }
    });
}

// Функция вызывается при изменении состояния плеера
function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {
        document.getElementById('youtube-container').style.display = 'none';
        document.getElementById('vk-container').style.display = 'block';
        requestFullScreen(document.getElementById('vk-container'));
    }
}

// Функция для запроса полноэкранного режима
function requestFullScreen(element) {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.mozRequestFullScreen) { // Firefox
        element.mozRequestFullScreen();
    } else if (element.webkitRequestFullscreen) { // Chrome, Safari and Opera
        element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) { // IE/Edge
        element.msRequestFullscreen();
    }
}

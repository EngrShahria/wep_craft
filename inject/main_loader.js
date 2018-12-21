var showLoader = function showLoader() {
  let text_block = {
      ru: 'Загрузка',
      en: 'Loading'
    },
    domain_zone = window.location.host.split('.').reverse()[0],
    default_language = {
      ru: 'ru',
      com: 'en'
    },
    html_block =
      `
  <div class="loader__block">
    <div class="loader__block__text">` +
      text_block[default_language[domain_zone]] +
      `</div>
    <div class="loader__block__center"></div>
    <div class="loader__block__lefttop"></div>
    <div class="loader__block__leftbot"></div>
    <div class="loader__block__righttop"></div>
    <div class="loader__block__rightbot"></div>
    <div class="loader__block__animation">
      <div class="frame_01"></div>
      <div class="frame_02"></div>
    </div>
  </div>
  `,
    loader_styles = `
  .loader__block {
    width: 366px;
    height: 118px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    font-family: 'Quantico', sans-serif;
    color: #fff;
    font-size: 36px;
    line-height: 118px;
    text-transform: uppercase;
  }
  .loader__block__lefttop,
  .loader__block__leftbot,
  .loader__block__righttop,
  .loader__block__rightbot,
  .loader__block__center {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    right: 0;
  }
  .loader__block__center:after,
  .loader__block__center:before {
    content: '';
    width: 62px;
    height: 2px;
    background: #f40;
    position: absolute;
    left: 152px;
  }
  .loader__block__center:after { top: -2px; }
  .loader__block__center:before { bottom: -2px; }
  .loader__block__lefttop:before,
  .loader__block__lefttop:after {
    content: '';
    background: #f40;
    position: absolute;
    left: -2px;
    top: -2px;
  }
  .loader__block__lefttop:before { width: 23px; height: 2px; }
  .loader__block__lefttop:after { width: 2px; height: 23px; }
  .loader__block__leftbot:before,
  .loader__block__leftbot:after {
    content: '';
    background: #f40;
    position: absolute;
    left: -2px;
    bottom: -2px;
  }
  .loader__block__leftbot:before { width: 23px; height: 2px; }
  .loader__block__leftbot:after { width: 2px; height: 23px; }
  .loader__block__righttop:before,
  .loader__block__righttop:after { content: '';
    background: #f40;
    position: absolute;
    right: -2px;
    top: -2px;
  }
  .loader__block__righttop:before { width: 23px; height: 2px; }
  .loader__block__righttop:after { width: 2px; height: 23px; }
  .loader__block__rightbot:before,
  .loader__block__rightbot:after {
    content: '';
    background: #f40;
    position: absolute;
    right: -2px;
    bottom: -2px;
  }
  .loader__block__rightbot:before { width: 23px; height: 2px; }
  .loader__block__rightbot:after { width: 2px; height: 23px; }
  .loader__block__animation {
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
  }
  .loader__block__animation .frame_01 {
    width: 320px;
    height: 72px;
    border: 2px solid #f40;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    opacity: 1;
    animation: frame-01 2s ease-out infinite;
  }
  .loader__block__animation .frame_02 {
    width: 318px;
    height: 70px;
    border: 1px solid #f40;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    opacity: 0;
    animation: frame-02 2s ease-in infinite;
  }
  @-moz-keyframes frame-01 {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1.05, 1.22); opacity: 0; }
  }
  @-webkit-keyframes frame-01 {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1.05, 1.22); opacity: 0; }
  }
  @-o-keyframes frame-01 {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1.05, 1.22); opacity: 0; }
  }
  @keyframes frame-01 {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1.05, 1.22); opacity: 0; }
  }
  @-moz-keyframes frame-02 {
    0% { opacity: 0; }
    10% { opacity: 0; }
    100% { opacity: 1; }
  }
  @-webkit-keyframes frame-02 {
    0% { opacity: 0; }
    10% { opacity: 0; }
    100% { opacity: 1; }
  }
  @-o-keyframes frame-02 {
    0% { opacity: 0; }
    10% { opacity: 0; }
    100% { opacity: 1; }
  }
  @keyframes frame-02 {
    0% { opacity: 0; }
    10% { opacity: 0; }
    100% { opacity: 1; }
  } `,
    head = document.head || document.getElementsByTagName('head')[0],
    style = document.createElement('style')

  style.type = 'text/css'

  if (style.styleSheet) {
    style.styleSheet.cssText = loader_styles
  } else {
    style.appendChild(document.createTextNode(loader_styles))
  }

  head.appendChild(style)

  document.querySelector('#loader').innerHTML = html_block
}

document.addEventListener('event::loadingStop', function() {
  document.querySelector('#loader').innerHTML = ''
  document.removeEventListener('event::loadingStop', function() {})
})

showLoader()

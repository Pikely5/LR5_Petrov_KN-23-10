// To display predictions, this app has:
// 1. A video that shows a feed from the user's webcam
// 2. A canvas that appears over the video and shows predictions
// When the page loads, a user is asked to give webcam permission.
// After this happens, the model initializes and starts to make predictions
// On the first prediction, an initialiation step happens in detectFrame()
// to prepare the canvas on which predictions are displayed.

// БЛОК ОБЪЯВЛЕНИЯ ГЛОБАЛЬНЫХ ПЕРЕМЕННЫХ
// Хранилище цветов для ограничивающих рамок каждого класса объектов
var bounding_box_colors = {};

// Пользовательский порог уверенности, начальное значение 0.6 (60%)
var user_confidence = 0.6;

// Список доступных цветов для отображения ограничивающих рамок распознанных объектов
var color_choices = [
  "#C7FC00",
  "#FF00FF",
  "#8622FF",
  "#FE0056",
  "#00FFCE",
  "#FF8000",
  "#00B7EB",
  "#FFFF00",
  "#0E7AFE",
  "#FFABAB",
  "#0000FF",
  "#CCCCCC",
];

// Флаг, указывающий была ли выполнена первая отрисовка на канвасе
var canvas_painted = false;
// Получение ссылки на элемент canvas из HTML-документа
var canvas = document.getElementById("video_canvas");
// Получение контекста рисования на canvas
var ctx = canvas.getContext("2d");

// БЛОК ИНИЦИАЛИЗАЦИИ ДВИЖКА ИНФЕРЕНСА
// Создание экземпляра движка инференса Roboflow
const inferEngine = new inferencejs.InferenceEngine();
// InferenceEngine - основной класс библиотеки inferencejs для загрузки и запуска моделей

// Идентификатор рабочего процесса модели, изначально отсутствует
var modelWorkerId = null;

// БЛОК ОБНАРУЖЕНИЯ ОБЪЕКТОВ НА КАДРЕ
// Функция захвата и обработки видеокадра
function detectFrame() {
  // Комментарий авторов паттерна: при первом запуске инициализируется канвас,
  // при всех запусках выполняется инференс с использованием видеокадра,
  // для каждого видеокадра отрисовываются ограничивающие рамки на канвасе

  // Проверка: если модель ещё не загружена, запланировать следующий кадр и выйти
  if (!modelWorkerId) return requestAnimationFrame(detectFrame);

  // Запуск инференса на текущем видеокадре
  // inferEngine.infer() - асинхронный метод, принимает идентификатор модели и изображение
  // CVImage - обёртка библиотеки inferencejs для представления изображений
  // predictions - массив результатов распознавания
  inferEngine.infer(modelWorkerId, new inferencejs.CVImage(video)).then(function(predictions) {

    // БЛОК ПЕРВОНАЧАЛЬНОЙ НАСТРОЙКИ КАНВАСА
    if (!canvas_painted) {
      // Если канвас ещё не настраивался
      var video_start = document.getElementById("video1");
      // Получение ссылки на видеоэлемент

      // Настройка позиционирования канваса поверх видео
      canvas.top = video_start.top;
      canvas.left = video_start.left;
      canvas.style.top = video_start.top + "px";
      canvas.style.left = video_start.left + "px";
      canvas.style.position = "absolute";
      // Отображение видеоэлемента и канваса
      video_start.style.display = "block";
      canvas.style.display = "absolute";
      canvas_painted = true;
      // Установка флага в true, чтобы настройка выполнилась только один раз

      var loading = document.getElementById("loading");
      loading.style.display = "none";
      // Скрытие индикатора загрузки после первого успешного кадра
    }

    // Планирование обработки следующего кадра
    requestAnimationFrame(detectFrame);
    // requestAnimationFrame - метод браузера для синхронизации с частотой обновления экрана

    // Очистка канваса от предыдущих результатов
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Если видео доступно, отрисовать ограничивающие рамки
    if (video) {
      drawBoundingBoxes(predictions, ctx)
    }
  });
}

// БЛОК ОТРИСОВКИ ОГРАНИЧИВАЮЩИХ РАМОК
// Функция отрисовки ограничивающих рамок вокруг распознанных объектов
function drawBoundingBoxes(predictions, ctx) {
  // Комментарий авторов паттерна: для каждого предсказания выбирается или назначается цвет
  // ограничивающей рамки, затем применяется необходимое масштабирование, чтобы рамки
  // отображались точно вокруг предсказанного объекта.
  // Если необходимо выполнить какие-либо действия с предсказаниями, начинайте с этой функции.
  // Например, можно отображать их на веб-странице, отмечать элементы в списке
  // или сохранять предсказания.

  // Цикл по всем предсказаниям модели
  for (var i = 0; i < predictions.length; i++) {
    // Получение значения уверенности для текущего предсказания
    var confidence = predictions[i].confidence;

    console.log(user_confidence)
    // Вывод текущего порога уверенности в консоль браузера

    // БЛОК ФИЛЬТРАЦИИ ПО ПОРОГУ УВЕРЕННОСТИ
    // Пропуск предсказаний, чья уверенность ниже заданного пользователем порога
    if (confidence < user_confidence) {
      continue
    }
    
    // БЛОК ВЫБОРА ЦВЕТА ДЛЯ КЛАССА ОБЪЕКТА
    // Постоянный цвет для одного и того же класса объектов
    if (predictions[i].class in bounding_box_colors) {
      // Если для класса уже назначен цвет, использовать его
      ctx.strokeStyle = bounding_box_colors[predictions[i].class];
    } else {
      // Если класс встретился впервые, выбрать случайный цвет из доступных
      var color =
        color_choices[Math.floor(Math.random() * color_choices.length)];
      ctx.strokeStyle = color;
      // Удалить выбранный цвет из списка доступных
      color_choices.splice(color_choices.indexOf(color), 1);
      // Сохранить назначенный цвет для класса
      bounding_box_colors[predictions[i].class] = color;
    }
    
    // БЛОК ВЫЧИСЛЕНИЯ КООРДИНАТ РАМКИ
    var prediction = predictions[i];
    // Координаты рамки: bbox содержит центр и размеры, пересчитываем в левый верхний угол
    var x = prediction.bbox.x - prediction.bbox.width / 2;
    var y = prediction.bbox.y - prediction.bbox.height / 2;
    var width = prediction.bbox.width;
    var height = prediction.bbox.height;

    // БЛОК ОТРИСОВКИ НА КАНВАСЕ
    // Установка прямоугольной области
    ctx.rect(x, y, width, height);
    // Заливка прозрачным цветом (рамка без заливки)
    ctx.fillStyle = "rgba(0, 0, 0, 0)";
    ctx.fill();
    // Установка стиля обводки и толщины линии
    ctx.fillStyle = ctx.strokeStyle;
    ctx.lineWidth = "4";
    // Отрисовка прямоугольной рамки
    ctx.strokeRect(x, y, width, height);
    // Настройка шрифта для текстовой подписи
    ctx.font = "25px Arial";
    // Отрисовка названия класса и процента уверенности над рамкой
    ctx.fillText(prediction.class + " " + Math.round(confidence * 100) + "%", x, y - 10);
  }
}

// БЛОК ИНИЦИАЛИЗАЦИИ ВЕБ-КАМЕРЫ
// Функция запроса доступа к веб-камере и запуска основного приложения
function webcamInference() {
   // Отображение индикатора загрузки
  var loading = document.getElementById("loading");
  loading.style.display = "block";

  // Запрос доступа к мультимедийным устройствам пользователя
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    // Параметр facingMode: "environment" указывает использовать заднюю камеру на мобильных устройствах
    .then(function(stream) {
      // Создание видеоэлемента для отображения потока с камеры
      video = document.createElement("video");
      video.srcObject = stream;
      // Привязка видеопотока к созданному элементу
      video.id = "video1";
      // Назначение идентификатора элементу

      // Скрытие видео до готовности веб-потока
      video.style.display = "none";
      video.setAttribute("playsinline", "");
      // playsinline разрешает воспроизведение видео внутри страницы на мобильных устройствах

      // Вставка видеоэлемента после канваса в DOM
      document.getElementById("video_canvas").after(video);

      // БЛОК ОБРАБОТКИ ЗАГРУЗКИ МЕТАДАННЫХ ВИДЕО
      video.onloadedmetadata = function() {
        video.play();
         // Запуск воспроизведения видео после загрузки метаданных
      }

      // БЛОК НАСТРОЙКИ РАЗМЕРОВ ПОСЛЕ НАЧАЛА ВОСПРОИЗВЕДЕНИЯ
      video.onplay = function() {
        // Получение реальных размеров видеопотока
        height = video.videoHeight;
        width = video.videoWidth;

        // Установка размеров видеоэлемента
        video.width = width;
        video.height = height;
        video.style.width = 640 + "px";
        video.style.height = 480 + "px";
        // Согласование размеров канваса с размерами видео
        canvas.style.width = 640 + "px";
        canvas.style.height = 480 + "px";
        canvas.width = width;
        canvas.height = height;
        // Отображение канваса
        document.getElementById("video_canvas").style.display = "block";
      };
      // Установка масштаба канваса
      ctx.scale(1, 1);

      // БЛОК ЗАГРУЗКИ МОДЕЛИ И ЗАПУСКА ИНФЕРЕНСА
      // Загрузка модели Roboflow с использованием публичного ключа и параметров из index.html
      inferEngine.startWorker(MODEL_NAME, MODEL_VERSION, publishable_key, [{ scoreThreshold: CONFIDENCE_THRESHOLD }])
        .then((id) => {
          // startWorker() загружает модель асинхронно
          // MODEL_NAME, MODEL_VERSION, publishable_key - глобальные переменные из index.html
          // scoreThreshold - минимальный порог уверенности для модели
          modelWorkerId = id;
          // Сохранение идентификатора рабочего процесса модели
          // Запуск функции обнаружения объектов
          detectFrame();
        });
    })
    .catch(function(err) {
      // Обработка ошибок доступа к камере
      console.log(err);
    });
}
// БЛОК ОБРАБОТКИ ПОЛЗУНКА УВЕРЕННОСТИ
// Функция изменения порога уверенности при перемещении ползунка
function changeConfidence () {
   // Получение значения ползунка (от 1 до 100) и преобразование в диапазон от 0.01 до 1.0
  user_confidence = document.getElementById("confidence").value / 100;
}

// БЛОК ПРИВЯЗКИ ОБРАБОТЧИКОВ СОБЫТИЙ
// Назначение обработчика события ввода на элемент ползунка
document.getElementById("confidence").addEventListener("input", changeConfidence);
// При каждом изменении положения ползунка вызывается функция changeConfidence

// БЛОК ЗАПУСКА ПРИЛОЖЕНИЯ
// Запуск функции инициализации веб-камеры и инференса
webcamInference();
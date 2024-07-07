from ultralytics import YOLO

class Model:

    model = YOLO("yolov8m.pt")
    detected_classes = {}
    class_elements = {}

    @staticmethod
    def predict(objects: list, display_img=False):
        results = Model.model(objects)
        classes = []
        for result in results:
            result.show() if display_img else ...
            classes.extend([int(element) for element in result.boxes.cls])
        Model.detected_classes = list(set(classes))
        Model.clasify_objects(results)
        return results
    
    @staticmethod
    def save_result(result, output_path):
        result.save(filename=output_path)


    @staticmethod
    def clasify_objects(results):
        Model.class_elements = {}
        for element in Model.detected_classes:
            Model.class_elements.update({results[0].names[element] : []})
        for box in results[0].boxes:
            Model.class_elements[results[0].names[int(box.cls)]].append(Model.calculate_xy_pos(box.xywh[0]))
        print(list(Model.class_elements.keys()))

    @staticmethod
    def get_detected_elements():
        detected_elements = {}
        for key, value in Model.class_elements.items():
            for id, element in enumerate(value):
                new_id = f"{key}_{id}"
                detected_elements.update({new_id : element})
        return detected_elements

    @staticmethod
    def get_results_position(result):
       return {id: Model.calculate_xy_pos(box) for id, box in enumerate(result[0].boxes.xywh)}

    @staticmethod
    def calculate_xy_pos(box):
        x_pos, y_pos, box_width, box_height = box[0], box[1], box[2], box[3]
        return (int(x_pos), int(y_pos))
// Imported: formatter, set_data, Crêpes2, crepelist from global
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
// Some useful Variables
var need_to_speichern = false;
var crepes_selected = false;
var edited_crepes_ids = [];
window.onbeforeunload = function () {
    if (need_to_speichern) {
        return "U SURE?";
    }
    else
        return;
};
var send_to_server_list = {
    new: new Array,
    edit: new Array,
    delete: new Array
};
function set_settings_up() {
    if (crepelist.length == 0) {
        var list = document.getElementById("crepes_list");
        var elems = list.querySelectorAll(".crepe_container");
        for (var i = 0; i < elems.length; i++) {
            var crepe = elems[i];
            var id = crepe.getAttribute("data-id");
            var name = crepe.getAttribute("data-name");
            var price = crepe.getAttribute('data-price');
            crepelist.push(new Crêpe2(id, name, price, 0, crepe));
        }
    }
}
function prepare_loader() {
    var button = document.getElementById('save_btn');
    var text = document.getElementById('save_text');
    var loader = document.getElementById('loader');
    button.addEventListener("mouseenter", function () {
        text.style.display = "none";
        loader.style.display = "block";
    });
    button.addEventListener("mouseout", function () {
        text.style.display = "block";
        loader.style.display = "none";
    });
}
set_settings_up();
prepare_loader();
/**
 * Function that is called by #save_btn
 */
function button_save_changes_to_server() {
    return __awaiter(this, void 0, void 0, function () {
        var save_btn;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    save_btn = document.getElementById('save_btn');
                    return [4 /*yield*/, save_changes()];
                case 1:
                    if (_a.sent()) {
                        save_btn.style.backgroundColor = "rgba(0, 255, 0, 1);";
                        save_btn.innerText = "Gespeichert!";
                        setTimeout(function () {
                            save_btn.style.backgroundColor = "auto;";
                            save_btn.innerText = "Speichern";
                        }, 2000);
                    }
                    return [2 /*return*/];
            }
        });
    });
}
function change_selected() {
    var select_elem = document.getElementById('color');
    var custom_select_elem = document.getElementById("ccolor");
    if (select_elem.value == 'custom') {
        select_elem.hidden = true;
        custom_select_elem.hidden = false;
    }
    var selected_color = select_elem.value;
    select_elem.style.backgroundColor = selected_color;
}
/**
 * Funktion prüft, ob die Liste mit Crêpes leer ist
 */
function check_if_empty() {
    if (document.getElementById('crepes_list').childElementCount == 0) {
        return true;
    }
    else {
        return false;
    }
}
/**
 * Checks, if crepes_list is empty and if it is, shows the empty elem instead.
 */
function toggle_empty() {
    var error_elem = document.getElementById('no_crepes');
    var list_elem = document.getElementById('crepes_list');
    if (check_if_empty()) {
        list_elem.style.display = "none";
        error_elem.style.display = "block";
    }
    else {
        list_elem.style.display = "block";
        error_elem.style.display = "none";
    }
}
/**
 * Entfernt crêpes von der liste und fügt sie der send_to_server_list an.
 * @param target Der Löschen Knopf
 */
function delte_crepe(target) {
    var root = target.parentElement.parentElement.parentElement;
    if (!('crepe_container' in root.classList)) {
        console.group("Error");
        console.error("FATAL ERROR. Function: delete_crepe");
        console.info(root);
        console.groupEnd();
    }
    var crepename = root.getAttribute('data-name');
    root.remove();
    toggle_empty();
    var id = root.getAttribute("data-id");
    send_to_server_list.delete.push({
        "id": id,
        "name": crepename
    });
    need_to_speichern = true;
    check_if_need_to_speichern();
}
function loadCrepe(elem, crepes_data) {
    var crepes_id = document.getElementById('editID');
    var crepes_name = document.getElementById('editCrepeName');
    var crepes_price = document.getElementById('editPrice');
    var crepes_ingredients = document.getElementById('editIngredients');
    if (elem.value == "select") {
        crepes_id.value, crepes_name.value, crepes_price.value, crepes_ingredients.value = "";
        crepes_selected = false;
        return;
    }
    var crêpes_name = elem.value;
    crepes_data.forEach(function (crepes) {
        if (crepes.name == crêpes_name) {
            console.log(crepes);
            crepes_id.value = crepes['id'];
            crepes_name.value = crepes['name'];
            crepes_price.value = crepes['price'];
            crepes_ingredients.value = crepes['ingredients'];
            return;
        }
    });
    crepes_selected = true;
}
function editCrepe() {
}
function create_crepe() {
    return __awaiter(this, void 0, void 0, function () {
        var name, price, ingredients, color, crepe_data;
        return __generator(this, function (_a) {
            console.log("Creating crêpes");
            name = document.getElementById('crepeName');
            price = document.getElementById('price');
            ingredients = document.getElementById('ingredients');
            color = document.getElementById('color');
            crepe_data = {
                // @ts-expect-error
                "name": name.value,
                // @ts-expect-error
                "price": price.value,
                // @ts-expect-error
                "ingredients": ingredients.value,
                // @ts-expect-error
                "color": color.value
            };
            console.log(crepe_data);
            send_to_server_list.new.push(crepe_data);
            need_to_speichern = true;
            check_if_need_to_speichern();
            return [2 /*return*/];
        });
    });
}
/**
 * **Bitte save_changes() benutzen**
 */
function send_to_server() {
    return __awaiter(this, void 0, void 0, function () {
        function send_delete() {
            return __awaiter(this, void 0, void 0, function () {
                var response, text;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0: return [4 /*yield*/, fetch("/api/crepes/delete", {
                                method: "DELETE",
                                mode: "cors",
                                cache: "no-cache",
                                credentials: "same-origin",
                                headers: { "Content-Type": "application/json" },
                                redirect: "manual",
                                referrerPolicy: "no-referrer",
                                body: JSON.stringify(send_to_server_list.delete)
                            })];
                        case 1:
                            response = _a.sent();
                            return [4 /*yield*/, response.text()];
                        case 2:
                            text = _a.sent();
                            if (response.ok) {
                                need_to_speichern = false;
                                console.log(text);
                                return [2 /*return*/, true];
                            }
                            else {
                                console.warn(text);
                                return [2 /*return*/, false];
                            }
                            return [2 /*return*/];
                    }
                });
            });
        }
        function send_edit() {
            return __awaiter(this, void 0, void 0, function () {
                var response, text;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0: return [4 /*yield*/, fetch("/api/crepes/edit", {
                                method: "PATCH",
                                mode: "cors",
                                cache: "no-cache",
                                credentials: "same-origin",
                                headers: { "Content-Type": "application/json" },
                                redirect: "manual",
                                referrerPolicy: "no-referrer",
                                body: JSON.stringify(send_to_server_list.edit)
                            })];
                        case 1:
                            response = _a.sent();
                            return [4 /*yield*/, response.text()];
                        case 2:
                            text = _a.sent();
                            if (response.ok) {
                                need_to_speichern = false;
                                console.log(text);
                                return [2 /*return*/, true];
                            }
                            else {
                                console.warn(text);
                                return [2 /*return*/, false];
                            }
                            return [2 /*return*/];
                    }
                });
            });
        }
        function send_new() {
            return __awaiter(this, void 0, void 0, function () {
                var response, text;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            console.log("Send new!");
                            return [4 /*yield*/, fetch("/api/crepes/new", {
                                    method: "PUT",
                                    mode: "cors",
                                    cache: "no-cache",
                                    credentials: "same-origin",
                                    headers: { "Content-Type": "application/json" },
                                    redirect: "manual",
                                    referrerPolicy: "no-referrer",
                                    body: JSON.stringify(send_to_server_list.new)
                                })];
                        case 1:
                            response = _a.sent();
                            return [4 /*yield*/, response.text()];
                        case 2:
                            text = _a.sent();
                            if (response.ok) {
                                need_to_speichern = false;
                                console.log(text);
                                return [2 /*return*/, true];
                            }
                            else {
                                console.warn(text);
                                return [2 /*return*/, false];
                            }
                            return [2 /*return*/];
                    }
                });
            });
        }
        var return_value;
        return __generator(this, function (_a) {
            console.log("Speichern");
            ;
            ;
            return_value = false;
            if (send_to_server_list.new.length >= 1) {
                return_value = true;
                send_new();
            }
            if (send_to_server_list.edit.length >= 1) {
                return_value = true;
                send_edit();
            }
            if (send_to_server_list.delete.length >= 1) {
                return_value = true;
                send_delete();
            }
            return [2 /*return*/, return_value];
        });
    });
}
/**
 * Sendet alles an den Server
 *
 * **Letzte funktion, die das Senden verhindern kann**
 */
function save_changes() {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            console.warn("Folgendes wird versandt: ");
            console.warn(send_to_server_list);
            if (!send_to_server()) {
                return [2 /*return*/, false];
            }
            return [2 /*return*/, true];
        });
    });
}
function check_if_need_to_speichern() {
    /**
     * Checks if send_to_server_list is empty
     */
    function is_all_empty() {
        if (send_to_server_list.delete.length != 0 && send_to_server_list.edit.length != 0 && send_to_server_list.new.length != 0) {
            return true;
        }
        else {
            return false;
        }
    }
    var btn = document.getElementById('save_btn');
    if (is_all_empty()) {
        btn.style.backgroundColor = "rgb(120, 120, 120)";
    }
    else {
        btn.style.backgroundColor = "rgb(0, 133, 35)";
    }
}
function input_changed(elem) {
    var container = elem.parentElement;
    var marker = container.getElementsByClassName("edited_hint")[0];
    var crepes_id = elem.getAttribute("data-id");
    elem.addEventListener("focusout", function () {
        if (elem.value != elem.defaultValue) {
            console.log("Something changed!");
            edited_crepes_ids.push(crepes_id);
        }
        else {
            console.log("Nothing changed!");
            if (crepes_id in edited_crepes_ids) {
                edited_crepes_ids.splice(edited_crepes_ids.indexOf(crepes_id), 1);
            }
        }
    }, { once: true });
    if (elem.value != elem.defaultValue) {
        container.setAttribute("was_edited", "true");
        marker.style.display = "block";
        need_to_speichern = true;
        check_if_need_to_speichern();
    }
    else {
        marker.style.display = "none";
        container.setAttribute("was_edited", "false");
        need_to_speichern = true;
        check_if_need_to_speichern();
    }
}
check_if_need_to_speichern();

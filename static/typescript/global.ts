/**
 * These are all urls pointing to the api. For quick access
 */
const urls = {
    newsale: "/api/sales/sold",
    resistor: "/api/sales/failResister",
    getsales: "/api/sales/get",
    
    getcrepes: "/api/crepes/get",
    delCrepe: "/api/crepes/delete",
    editCrepe: "/api/crepes/edit",
    newCrepe: "/api/crepes/new",
}

var api_key = "";

if (localStorage.getItem("auth") == null) {
    window.location.assign("/init");
} else {
    api_key = localStorage.getItem("auth")
}


async function send_server(url: string, method: string, body?: any): Promise<Response> {
    var response: Promise<Response> | Response;
    try {
        if (body != undefined) {
            response = await fetch(url, {
                method: method,
                mode: "same-origin",
                cache: "no-cache",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-crepeAuth": api_key
                },
                redirect: "manual",
                referrerPolicy: "no-referrer",
                body: JSON.stringify(body)
            })
        } else {
            response = await fetch(url, {
                method: method,
                mode: "same-origin",
                cache: "no-cache",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-crepeAuth": api_key
                },
                redirect: "manual",
                referrerPolicy: "no-referrer",
            })
    
        }
    } catch (error) {
        alert("Es gab einen Fehler!")
        throw {"name": "Error"}
    }

    if (response.status == 304) {
        localStorage.removeItem("auth")
        location.reload()
    }

    return response
}

var crepelist: Crêpe[] = []
var crepemap: Map<Crêpe, Map<unknown, unknown>> = new Map();

var connectionError: boolean = false;


class Crêpe {
    id: number;
    name: string;
    preis: number;
    crepeId: number;
    amount: number;
    color: string;
    root_element: HTMLElement;
    table_element: HTMLTableElement | undefined = undefined;

    constructor(id: number, name: string, preis: number, amount: number, color?: string, root_element?: HTMLElement, table_root_element?: HTMLTableElement) {
        this.crepeId = id;
        this.name = name;
        this.preis = preis;
        this.amount = amount;
        this.color = color;
        this.root_element = root_element;
        this.table_element = table_root_element;
    }

    public toString() {
        return `\n${this.crepeId} ; ${this.name} ; ${this.preis} ; ${this.amount}\n`
    }
}

/**
 * Adds all crêpes to the crepelist
 * @param root_element The root element of the crepe
 * @param crepeId The id of the crepe
 * @param crepeName The name of the crepe
 * @param crepePreis the Price of the crepe
 * @returns Nothing
 */
function set_data(root_element: HTMLElement, crepeId?: string, crepeName?: string, crepePreis?: number) {
    if (crepeName == undefined && crepePreis == undefined && crepeId == undefined) {
        crepeName = root_element.getAttribute('data-name')
        crepePreis = (root_element.getAttribute('data-preis')) as unknown as number
        crepeId = (root_element.getAttribute('data-id'))
    }

    crepelist.push(new Crêpe(Number(crepeId), crepeName, Number(crepePreis), 0, null, root_element))
    return;
}


/**
 * For formatting number to currency
 */
const formatter = new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
})

/**
 * Updates the small amount hint below the crepecontrol
 * @param root The Crêpes' root element
 * @param new_amount The value to update to
 */
function handle_amount_counter(root: HTMLElement, new_amount: number) {
    const counter = root.querySelector(".crepecontrol .crepes_counter") as HTMLElement
    if (new_amount == 0) {
        counter.innerHTML = ""
    } else {
        counter.innerHTML = String(new_amount) + "x"
    }
}
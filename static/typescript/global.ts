const urls = {
    newSale: "/api/sold",
    resistor: "/api/sold/failresistor",
}

var crepelist: Crêpe[] = []
var crepemap: Map<Crêpe, Map<unknown, unknown>> = new Map();

var connectionError: boolean = false;

/**
 * either true or false
 */
class CrepeConError {
    value: boolean;

    constructor(value?: boolean) {
        this.value = value;
    }

    get () {
        return this.value;
    }

    setFavicon() {
        if (this.value) {

        }
    }
}

class Crêpe {
    id: number;
    name: string;
    preis: number;
    crepeId: number;
    amount: number;
    root_element: HTMLElement;
    table_element: HTMLTableElement | undefined = undefined;

    constructor(id: number, name: string, preis: number, amount: number, root_element: HTMLElement, table_root_element?: HTMLTableElement) {
        this.crepeId = id;
        this.name = name;
        this.preis = preis;
        this.amount = amount;
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

    crepelist.push(new Crêpe(Number(crepeId), crepeName, Number(crepePreis), 0, root_element))
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
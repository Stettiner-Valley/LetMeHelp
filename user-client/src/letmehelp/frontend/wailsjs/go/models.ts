export namespace main {
	
	export class KeyCombo {
	    Key: string;
	    Modifiers: string[];
	
	    static createFrom(source: any = {}) {
	        return new KeyCombo(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Key = source["Key"];
	        this.Modifiers = source["Modifiers"];
	    }
	}
	export class RunningApplication {
	    ProcessID: number;
	    Name: string;
	
	    static createFrom(source: any = {}) {
	        return new RunningApplication(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ProcessID = source["ProcessID"];
	        this.Name = source["Name"];
	    }
	}

}


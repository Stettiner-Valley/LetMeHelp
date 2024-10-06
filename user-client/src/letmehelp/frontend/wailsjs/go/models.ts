export namespace main {
	
	export class ApplicationBoundingBox {
	    top: number;
	    left: number;
	    bottom: number;
	    right: number;
	    PID: number;
	
	    static createFrom(source: any = {}) {
	        return new ApplicationBoundingBox(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.top = source["top"];
	        this.left = source["left"];
	        this.bottom = source["bottom"];
	        this.right = source["right"];
	        this.PID = source["PID"];
	    }
	}
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
	    ProcessName: string;
	    WindowTitle: string;
	
	    static createFrom(source: any = {}) {
	        return new RunningApplication(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ProcessID = source["ProcessID"];
	        this.ProcessName = source["ProcessName"];
	        this.WindowTitle = source["WindowTitle"];
	    }
	}

}


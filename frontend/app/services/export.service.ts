import { Injectable } from "@angular/core";
import {
  HttpClient,
  HttpEvent,
  HttpHeaders,
  HttpRequest,
  HttpEventType,
  HttpErrorResponse
} from "@angular/common/http";
import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { filter } from "rxjs/operator/filter";
import { map } from "rxjs/operator/map";

import { AppConfig } from "@geonature_config/app.config";


export interface Export {
  label: string;
  id: string;
  date: Date;
  standard: string;
  selection: string;
  extension: string;
}

export interface ExportLabel {
  label: string;
  date: Date;
}

const apiEndpoint='http://localhost:8000/interop';

export const StandardMap = new Map([
  ['NONE', 'RAW',],
  ['SINP', 'SINP'],
  ['DWC',  'DarwinCore'],
  // ['ABCD', 'ABCD Schema'],
  // ['EML',  'EML']
])

export const FormatMapMime = new Map([
  ['csv', 'text/csv'],
  ['json', 'application/json'],
  ['rdf', 'application/rdf+xml']
])

@Injectable()
export class ExportService {
  exports: BehaviorSubject<Export[]>
  labels: BehaviorSubject<ExportLabel[]>
  downloadProgress: BehaviorSubject<number>
  private _blob: Blob

  constructor(private _api: HttpClient) {
    this.exports = <BehaviorSubject<Export[]>>new BehaviorSubject([]);
    this.labels = <BehaviorSubject<ExportLabel[]>>new BehaviorSubject([]);
    this.downloadProgress = <BehaviorSubject<number>>new BehaviorSubject(0.0);
  }

  // FIXME: loader ?
  getExports() {
    this._api.get(`${apiEndpoint}/exports`).subscribe(
      (exports: Export[]) => this.exports.next(exports),
      error => console.error(error),
      () => {
        console.info(`export service: got ${this.exports.value.length} exports`)
        console.debug('exports:',  this.exports.value)
        this.getLabels()
      }
    )
  }

  getLabels() {

    function byLabel (a, b) {
      const labelA = a.label.toUpperCase()
      const labelB = b.label.toUpperCase()
      return (labelA < labelB) ? -1 : (labelA > labelB) ? 1 : 0
    }

    let labels = []
    this.exports.subscribe(xs => xs.map((x) => labels.push({label: x.label, date: x.date})))
    let seen = new Set()
    let uniqueLabels = labels.filter((item: ExportLabel) => {
                                let k = item.label
                                return seen.has(k) ? false : seen.add(k)
                              })
    this.labels.next(uniqueLabels.sort(byLabel))
  }

  downloadExport(submissionID: number, standard: string, extension: string) {
    const downloadExportURL = `${apiEndpoint}/exports/export_${standard}_${submissionID}.${extension}`
    let source = this._api.get(downloadExportURL, {
      headers: new HttpHeaders().set('Content-Type', `${FormatMapMime.get(extension)}`),
      observe: 'events',
      responseType: 'blob',
      reportProgress: true,
    })
    let subscription = source.subscribe(
      event => {
        if (event.type === HttpEventType.DownloadProgress) {
          if (event.hasOwnProperty('total')) {
            const percentage = Math.round((100 / event.total) * event.loaded);
            this.downloadProgress.next(percentage)
            console.debug(`Downloaded ${percentage}%.`);
          } else {
            const kb = Number.parsefloat(event.loaded / 1024).toFixed(2);
             this.downloadProgress.next(kb)
            console.debug(`Downloaded ${kb}Kb.`);
          }
      }
      if (event.type === HttpEventType.Response) {
        this._blob = new Blob([event.body], {type: event.headers.get('Content-Type')});
      }
    },
    (e: HttpErrorResponse) => {
      console.error(e.error);
      console.error(e.name);
      console.error(e.message);
      console.error(e.status);
    },
    () => this.saveBlob(this._blob, `export_${standard}_${submissionID}.${extension}`)
  )}

  saveBlob(blob, filename) {
    let link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.setAttribute('visibility','hidden')
    link.download = filename
    link.onload = function() { URL.revokeObjectURL(link.href) }
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

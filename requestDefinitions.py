"""
These are the request JSON-Strings as well as evalution functions for the API calls.
These have been kept simple as processing is done in python.
"""
EVALSCRIPT_RGB_IMAGE = """
//VERSION=3
function setup() {
  return {
    input: [
      {
        bands: ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"],
        units: "DN",
      },
    ],
    output: {
      bands: 12,
      sampleType: SampleType.FLOAT32,
    }
  }
}

function evaluatePixel(sample) {
  return [sample.B01, sample.B02, sample.B03, sample.B04, sample.B05, sample.B06, sample.B07, sample.B8A, sample.B09, sample.B10, sample.B11, sample.B12];
}
"""


EVALSCRIPT_DEM = """
//VERSION=3
function setup() {
  return {
    input: ["DEM"],
    output: {
      id: "default",
      bands: 1,
      sampleType: SampleType.FLOAT32,
    },
  }
}

function evaluatePixel(sample) {
  return [sample.DEM]
}
"""
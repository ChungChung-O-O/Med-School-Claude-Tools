#!/usr/bin/env node
"use strict";

const fs = require("fs");

function usage(message) {
  if (message) console.error(`ERROR: ${message}`);
  console.error("Usage: node validate_batch.js BATCH.json --bank BANK.json [--reference FILE ...] [--holdouts FILE] [--require-holdouts]");
  process.exit(message ? 2 : 0);
}

function readJson(path, label) {
  try {
    return JSON.parse(fs.readFileSync(path, "utf8"));
  } catch (error) {
    throw new Error(`${label} could not be read as JSON: ${error.message}`);
  }
}

function asQuestions(value, label) {
  const questions = Array.isArray(value) ? value : value && value.questions;
  if (!Array.isArray(questions)) throw new Error(`${label} must be a JSON array or an object with a questions array.`);
  return questions;
}

function words(value) {
  const stop = new Set(["a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "or", "the", "to", "which", "with"]);
  return new Set(String(value).toLowerCase().replace(/<[^>]*>/g, " ").replace(/[^a-z0-9]+/g, " ").split(/\s+/).filter(word => word.length > 2 && !stop.has(word)));
}

function jaccard(left, right) {
  const a = words(left), b = words(right);
  if (!a.size || !b.size) return 0;
  let overlap = 0;
  for (const word of a) if (b.has(word)) overlap += 1;
  return overlap / (a.size + b.size - overlap);
}

function optionSignature(question) {
  if (!question || !Array.isArray(question.options)) return "";
  return [...question.options].map(option => String(option).trim().toLowerCase()).sort().join("\u0000");
}

function validateQuestion(question, index, bankIds, bankBlocks, errors) {
  const label = question && question.id ? question.id : `question ${index + 1}`;
  if (!question || typeof question !== "object" || Array.isArray(question)) {
    errors.push(`${label}: must be an object.`); return;
  }
  const strings = ["id", "topic", "src", "stem", "rationale", "unit", "course", "source", "sourceRef", "variantAngle"];
  for (const field of strings) if (typeof question[field] !== "string" || !question[field].trim()) errors.push(`${label}: ${field} must be a non-empty string.`);
  if (typeof question.rationale === "string" && question.rationale.replace(/<[^>]*>/g, "").trim().length < 48) errors.push(`${label}: rationale must give a substantive overall teaching explanation.`);
  if (typeof question.context !== "string") errors.push(`${label}: context must be a string, even when empty.`);
  if (!/^MQG-[A-Z0-9][A-Z0-9.-]*-\d{2}$/.test(question.id || "")) errors.push(`${label}: id must match MQG-<SOURCE-OR-OBJECTIVE>-<NN>.`);
  if (bankIds.has(question.id)) errors.push(`${label}: id already exists in the released bank.`);
  if (question.type !== "mcq") errors.push(`${label}: only mcq candidates are supported.`);
  if (question.course !== "OST520" || !/^UE\d+$/.test(question.unit || "")) errors.push(`${label}: course/unit must identify an OST520 UE shelf.`);
  if (question.unit === "UE2") {
    if (typeof question.sourceBlock !== "string" || !question.sourceBlock.trim()) errors.push(`${label}: UE2 candidates require a non-empty sourceBlock.`);
    else if (!bankBlocks.has(question.sourceBlock)) errors.push(`${label}: sourceBlock must match a released UE2 block.`);
  }
  if (question.source !== "missed-remediation") errors.push(`${label}: source must be missed-remediation.`);
  if (question.holdout !== false) errors.push(`${label}: holdout must be false.`);
  if (question.requiresMedia !== false) errors.push(`${label}: requiresMedia must be false for release-ready remediation.`);
  for (const field of ["concepts", "covers"]) {
    if (!Array.isArray(question[field]) || !question[field].length || question[field].some(value => typeof value !== "string" || !value.trim())) errors.push(`${label}: ${field} must be a non-empty string array.`);
  }
  if (!Array.isArray(question.options) || question.options.length !== 5 || question.options.some(option => typeof option !== "string" || option.trim().length < 2)) {
    errors.push(`${label}: options must contain five non-empty strings.`);
  } else if (new Set(question.options.map(option => option.trim().toLowerCase())).size !== 5) {
    errors.push(`${label}: options must be unique.`);
  }
  if (!Number.isInteger(question.answer) || question.answer < 0 || question.answer >= 5) errors.push(`${label}: answer must be a zero-based index from 0 to 4.`);
  if (!Array.isArray(question.optionExplanations) || question.optionExplanations.length !== 5) {
    errors.push(`${label}: optionExplanations must contain five aligned entries.`);
  } else {
    question.optionExplanations.forEach((explanation, optionIndex) => {
      if (typeof explanation !== "string" || explanation.trim().length < 24) errors.push(`${label}: optionExplanations[${optionIndex}] must be a substantive string aligned with options[${optionIndex}].`);
    });
  }
  const ancestry = Array.isArray(question.derivedFrom) && question.derivedFrom.length;
  const description = typeof question.missDescription === "string" && question.missDescription.trim();
  if (!ancestry && !description) errors.push(`${label}: provide derivedFrom or missDescription.`);
  if (ancestry) question.derivedFrom.forEach(id => { if (!bankIds.has(id)) errors.push(`${label}: derivedFrom id ${id} is not in the released bank.`); });
}

function compare(candidate, references, privateReference, errors) {
  const exactStem = String(candidate.stem).trim().toLowerCase();
  const signature = optionSignature(candidate);
  references.filter(reference => reference && typeof reference === "object").forEach(reference => {
    const refLabel = privateReference ? "a private holdout" : `released item ${reference.id || "(unknown id)"}`;
    if (exactStem === String(reference.stem || "").trim().toLowerCase()) errors.push(`${candidate.id}: stem duplicates ${refLabel}.`);
    const similarity = jaccard(candidate.stem, reference.stem || "");
    if (similarity >= 0.72) errors.push(`${candidate.id}: stem is too similar to ${refLabel} (${similarity.toFixed(2)}).`);
    if (signature && signature === optionSignature(reference)) errors.push(`${candidate.id}: option set duplicates ${refLabel}.`);
  });
}

function validate(batch, bank, holdouts, extraReferences = []) {
  const errors = [], bankIds = new Set(bank.map(question => question.id));
  const bankById = new Map(bank.map(question => [question.id, question]));
  const bankBlocks = new Set(bank.filter(question => question.unit === "UE2" && typeof question.sourceBlock === "string").map(question => question.sourceBlock));
  const extraIds = new Set(extraReferences.map(question => question.id));
  const holdoutIds = new Set(holdouts.map(question => question.id));
  const batchIds = new Set();
  batch.forEach((question, index) => {
    validateQuestion(question, index, bankIds, bankBlocks, errors);
    if (question && batchIds.has(question.id)) errors.push(`${question.id}: duplicate id inside batch.`);
    if (question && extraIds.has(question.id)) errors.push(`${question.id}: id already exists in another staged, reserved, or media-gated collection.`);
    if (question && holdoutIds.has(question.id)) errors.push(`${question.id}: id collides with a private holdout.`);
    if (question && Array.isArray(question.derivedFrom) && question.derivedFrom.length) {
      const parents = question.derivedFrom.map(id => bankById.get(id)).filter(Boolean);
      const parentConcepts = new Set(parents.flatMap(parent => parent.concepts || []));
      const parentCovers = new Set(parents.flatMap(parent => parent.covers || []));
      if (!Array.isArray(question.concepts) || !question.concepts.some(concept => parentConcepts.has(concept))) errors.push(`${question.id}: concepts must retain at least one concept from derivedFrom.`);
      if (!Array.isArray(question.covers) || !question.covers.some(objective => parentCovers.has(objective))) errors.push(`${question.id}: covers must retain at least one objective from derivedFrom.`);
      const parentBlocks = new Set(parents.map(parent => parent.sourceBlock).filter(Boolean));
      if (question.unit === "UE2" && parentBlocks.size && !parentBlocks.has(question.sourceBlock)) errors.push(`${question.id}: sourceBlock must inherit a block from derivedFrom.`);
    }
    if (question) batchIds.add(question.id);
  });
  batch.forEach((question, index) => {
    if (!question || !Array.isArray(question.options) || question.options.length !== 5) return;
    compare(question, bank, false, errors);
    compare(question, extraReferences, false, errors);
    compare(question, holdouts, true, errors);
    compare(question, batch.slice(0, index), false, errors);
  });
  return errors;
}

function selfTest() {
  const bank = [{id:"B1",stem:"Which enzyme converts alpha into beta during fasting?",options:["one","two","three","four","five"],unit:"UE2",sourceBlock:"L001",concepts:["test-concept"],covers:["L001"]}];
  const candidate = {id:"MQG-L001-01",topic:"Biochemistry",src:"B",stem:"A fasting patient cannot convert gamma into delta. Which enzyme is impaired?",options:["A enzyme","B enzyme","C enzyme","D enzyme","E enzyme"],answer:1,optionExplanations:[
    "This enzyme acts in a different pathway and cannot explain the stated block.",
    "This enzyme catalyzes the blocked step described in the clinical scenario.",
    "This enzyme acts downstream, so its loss would produce a different metabolite pattern.",
    "This enzyme performs the reverse reaction under a different physiologic condition.",
    "This enzyme regulates the pathway but does not catalyze the missing conversion."
  ],rationale:"The metabolite pattern localizes the defect to the enzyme that directly catalyzes the blocked step.",type:"mcq",context:"",unit:"UE2",course:"OST520",concepts:["test-concept"],covers:["L001"],source:"missed-remediation",sourceRef:"Test source, slide 1",sourceBlock:"L001",derivedFrom:["B1"],missDescription:"",variantAngle:"Infer the enzyme from a metabolite pattern.",holdout:false,requiresMedia:false};
  let errors = validate([candidate], bank, []);
  if (errors.length) throw new Error(`self-test valid candidate failed: ${errors.join(" | ")}`);
  const broken = JSON.parse(JSON.stringify(candidate)); broken.id = "B1";
  broken.optionExplanations[0] = "short";
  errors = validate([broken], bank, []);
  if (!errors.some(error => error.includes("already exists")) || !errors.some(error => error.includes("substantive string"))) throw new Error("self-test did not reject identity and explanation failures.");
  const malformed = JSON.parse(JSON.stringify(candidate)); malformed.concepts = "test-concept"; malformed.covers = "L001"; delete malformed.sourceBlock;
  errors = validate([null, {id:"MQG-L028-98"}, malformed, candidate], bank, []);
  if (!errors.some(error => error.includes("UE2 candidates require")) || !errors.some(error => error.includes("concepts must be")) || !errors.some(error => error.includes("covers must be"))) throw new Error("self-test did not reject malformed UE2 routing fields.");
  console.log("PASS: validator self-test");
}

function main(argv) {
  if (argv.includes("--self-test")) return selfTest();
  const batchPath = argv[0];
  if (!batchPath || batchPath.startsWith("-")) usage("BATCH.json is required.");
  let bankPath, holdoutPath;
  const referencePaths = [];
  for (let i = 1; i < argv.length; i += 1) {
    if (argv[i] === "--bank") bankPath = argv[++i];
    else if (argv[i] === "--reference") referencePaths.push(argv[++i]);
    else if (argv[i] === "--holdouts") holdoutPath = argv[++i];
    else if (argv[i] !== "--require-holdouts") usage(`Unknown argument: ${argv[i]}`);
  }
  if (!bankPath) usage("--bank BANK.json is required.");
  if (argv.includes("--require-holdouts") && !holdoutPath) usage("--require-holdouts needs --holdouts FILE.");
  if (holdoutPath && !fs.existsSync(holdoutPath)) usage("The private holdout file does not exist.");
  const batchValue = readJson(batchPath, "batch"), batch = asQuestions(batchValue, "batch");
  const bank = asQuestions(readJson(bankPath, "bank"), "bank");
  const holdouts = holdoutPath ? asQuestions(readJson(holdoutPath, "private holdouts"), "private holdouts") : [];
  if (argv.includes("--require-holdouts") && !holdouts.length) usage("The required private holdout collection is empty.");
  const extraReferences = referencePaths.flatMap((path, index) => asQuestions(readJson(path, `reference ${index + 1}`), `reference ${index + 1}`));
  const errors = validate(batch, bank, holdouts, extraReferences);
  if (errors.length) {
    errors.forEach(error => console.error(`ERROR: ${error}`));
    process.exit(1);
  }
  console.log(`PASS: ${batch.length} candidate question(s); ${bank.length} released reference(s); ${extraReferences.length} additional reference(s); private holdouts checked: ${holdouts.length}.`);
}

if (require.main === module) main(process.argv.slice(2));
module.exports = { jaccard, validate };

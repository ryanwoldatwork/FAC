class searchPage 
{
constructor() {
    this.auditYearCheckbox = '#audit-year input[type="checkbox"]';
    //define a function 'yearCheckboxById' that takes a 'year' argument. Using a dynamic selector.
    this.yearCheckboxById = (year) => (year.toLowerCase() === 'all_years' ? '#audit-year [id^="audit-year-"]' : `#audit-year-${year}`);
    this.accordionButton = '.usa-accordion__button';
    this.ueiOrEinField = '#uei-or-ein';
    this.alnField = '#aln';
    this.entityNameField = '#entity-name';
    this.startDateField = '#start-date';
    this.endDateField = '#end-date';
    this.auditeeState = '#auditee_state';
    this.optionsField = '#options';
    this.findingsAccordionButton = '.usa-accordion__button:contains("Audit findings")';
    this.auditFindingsCheckbox = '#usa-checkbox__input[value="${value}"]';
    this.findingsCheckboxId = (findings) => `.usa-checkbox__input[value="${findings.toLowerCase()}"]`;
    this.directFundingAccordionButton = '.usa-accordion__button:contains("Direct funding")';
    this.directFundingCheckbox = '#usa-checkbox__input[value="${value}"]';
    this.directFundingCheckboxId = (funding) => `.usa-checkbox__input[value="${funding.toLowerCase()}"]`;
    this.majorProgramAccordionButton = '.usa-accordion__button:contains("Major program")';
    this.majorProgramRadio = '.usa-radio__input[name="major_program"]';
    this.searchSubmitButton = 'input.usa-button[type="submit"][value="Search"]';

}

checkAuditYearCheckbox(year){
    cy.get(this.yearCheckboxById(year)).check({force: true}).should('be.checked').and('have.value', year);
}

uncheckAuditYearCheckbox(year){
    cy.get(this.yearCheckboxById(year)).uncheck({force: true}).should('not.be.checked').and('have.value', year);
}

testUEIorEin(value) {
    cy.get(this.accordionButton).contains('UEI or EIN').as('accordionButton').click();
    cy.get(this.ueiOrEinField).clear().type(value);
}

testALN(value) {
    cy.get(this.accordionButton).contains('Assistance Listing Number (formerly CFDA').as('accordionButton').click();
    cy.get(this.alnField).clear().type(value);
}

testName(value) {
    cy.get(this.accordionButton).contains('Name (Entity, Auditee, or Auditor)').as('accordionButton').click();
    cy.get(this.entityNameField).clear().type(value);
}

testFACacceptanceDate(startDate, endDate) {
    cy.get(this.accordionButton).contains('FAC acceptance date').as('accordionButton').click();
    cy.get(this.startDateField).clear().type(startDate);
    cy.get(this.endDateField).clear().type(endDate);
}

testState(value) {
    cy.get(this.accordionButton).contains('State').as('accordionButton').click();
    cy.get(this.auditeeState).select(value);
}

testCogorOver(value) {
    cy.get(this.accordionButton).contains('Cognizant or Oversight').as('accordionButton').click();
    cy.get(this.optionsField).select(value);
}

testCogorOver(value) {
    cy.get(this.accordionButton).contains('Cognizant or Oversight').as('accordionButton').click();
    cy.get(this.optionsField).select(value);
}

openFindingsAccordion() {
    cy.get(this.findingsAccordionButton).as('accordionButton').click();
}

checkAuditFindingsCheckbox(findings){
    cy.get(this.findingsCheckboxId(findings)).check({force: true}).should('be.checked').and('have.value', findings);
}

uncheckAuditFindingsCheckbox(findings){
    cy.get(this.findingsCheckboxId(findings)).uncheck({force: true}).should('not.be.checked').and('have.value', findings);
}

openDirectFundingAccordion() {
    cy.get(this.directFundingAccordionButton).as('accordionButton').click();
}

checkDirectFundingCheckbox(funding){
    cy.get(this.directFundingCheckboxId(funding)).check({force: true}).should('be.checked').and('have.value', funding);
}

uncheckDirectFundingCheckbox(funding){
    cy.get(this.directFundingCheckboxId(funding)).uncheck({force: true}).should('not.be.checked').and('have.value', funding);
}

openMajorProgramAccordion() {
    cy.get(this.majorProgramAccordionButton).as('accordionButton').click();
}

checkMajorProgramRadio(value){
    cy.get(`${this.majorProgramRadio}[value="${value}"]`).check({force: true}).should('be.checked').and('have.value', value);
}

uncheckMajorProgramRadio(value){
    cy.get(`${this.majorProgramRadio}[value="${value}"]`).check({force: true}).should('be.checked').and('have.value', value);
}

testSearchSubmitButton(){
    cy.get(`${this.searchSubmitButton}:last`).click();
}

}

export default searchPage;
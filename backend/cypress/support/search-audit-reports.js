
const yearsToCheck = ['2023','2022','2021','2020','2019','2018','2017','2016'];

export function testSearch(){
    cy.visit('/dissemination/search/');
    //cy.get('#audit-year-2023').check({force: true}).should('be.checked').and('have.value','2023');
   // cy.get('#audit-year-2023').uncheck({force: true}).should('not.be.checked');
    //cy.get('input[type="checkbox"]').check(['2022','2021']);
    cy.get('input[type="checkbox"]').each((checkbox, index) => {
        const year = yearsToCheck[index];
        cy.wrap(checkbox).check({ force: true}).should('have.value',year);
        //cy.get('#uei-or-ein').clear().type('D7A4J33FUMJ1');
    });

    cy.get('#uei-or-ein').clear().type('D7A4J33FUMJ1');
    cy.get('#aln').clear().type('93');
    //cy.get('#entity-name').clear().type('');

    cy.get('#start-date').type('02/01/2024');
    cy.get('#end-date').type('02/28/2024');

    cy.get('#options').select('oversight').should('have.value','oversight');

    cy.get('#agency-name').type('93');

    cy.get('#auditee_state').select('VA').should('have.value','VA');

    cy.get(':nth-child(4) > [type="submit"]').should('have.value','Search').click();
    cy.url().should('match', /\/dissemination\/search\//);

}
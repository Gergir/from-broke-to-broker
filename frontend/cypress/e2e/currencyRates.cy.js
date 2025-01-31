describe('Testing rates page', () => {
    it('Should open the page', () => {
        cy.visit('/');
        cy.get('button').contains('Initialize Rates').click();
        cy.get('h1').should('contain', 'Currency Rates');
    });
    it('Should try to press buttons for which, there will no data to get', () => {
        cy.visit('/');
        cy.get('h1').should('contain', 'Currency Rates');
        cy.get('button').contains('Year').click();
        cy.get('.react-datepicker__year-text').contains('2026').click();
        cy.get('button').contains('Fetch Rates').click();
        cy.get('.error').contains('Date cannot be in the future.').should('exist');
        cy.get('button').contains('Show Rates').click();
        cy.get('.error').contains('Date cannot be in the future.').should('exist');

    });
    it('should try to get not existing rates', () => {
        cy.visit('/');
        cy.get('h1').should('contain', 'Currency Rates');
        cy.get('.period-button').contains('Month').click();
        cy.get('.react-datepicker__navigation--previous').click();
        cy.get('.react-datepicker__month-text').contains('Dec').click();
        cy.get('button').contains('Show Rates').click();
        cy.get('.error').contains('No rates found for the requested period. Try to download them first.')
            .should('exist');
    });
    it('should try to fetch rates twice', () => {
        cy.visit('/');
        cy.get('h1').should('contain', 'Currency Rates');
        cy.get('.period-button').contains('Month').click();
        cy.get('.react-datepicker__navigation--previous').click();
        cy.get('.react-datepicker__month-text').contains('Nov').click();
        cy.get('select').select('USD');
        cy.get('select').should('have.value', 'USD')
        cy.get('button').contains('Show Rates').click();
        cy.get('.error').contains('No USD rates found for the requested period. Try to download them first.')
            .should('exist');
        cy.get('button').contains('Fetch Rates').click();
        cy.get('button').contains('Fetch Rates').click();
        cy.get('.error').contains('All USD rates for specified period are already in the database.').should('exist');
    });

    it('fetch rates, check if rates are in table and chart is present', () => {
        cy.visit('/');
        cy.get('h1').should('contain', 'Currency Rates');
        cy.get('.period-button').contains('Month').click();
        cy.get('.react-datepicker__navigation--previous').click();
        cy.get('.react-datepicker__month-text').contains('Dec').click();
        cy.get('select').select('EUR');
        cy.get('select').should('have.value', 'EUR')
        cy.get('button').contains('Fetch Rates').click();  // Fetch also trigger get rates (after being successful)
        cy.get('canvas').should('exist');
        cy.get('table').should('exist');
    });

});